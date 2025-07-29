# Copyright 2022 Dynatrace LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional, Set

from dynatrace.opentelemetry.tracing._config.reader import get_configuration
from dynatrace.opentelemetry.tracing._logging.loggers import propagator_logger
from dynatrace.opentelemetry.tracing._otel.api import (
    DEFAULT_TRACE_STATE,
    INVALID_SPAN_CONTEXT,
    CarrierT,
    Context,
    Getter,
    NonRecordingSpan,
    Setter,
    SpanContext,
    TextMapPropagator,
    TraceContextTextMapPropagator,
    TraceFlags,
    TraceState,
    default_getter,
    default_setter,
    get_current_span,
    set_span_in_context,
)
from dynatrace.opentelemetry.tracing._propagator.tags import (
    Fw4Tag,
    RumTag,
    get_trace_state_key,
)
from dynatrace.opentelemetry.tracing._propagator.textmapcodec import (
    from_trace_state,
    parse_x_dynatrace,
    to_trace_state_value,
    to_x_dynatrace,
)
from dynatrace.opentelemetry.tracing._util.context import set_ctx_rum_tag
from dynatrace.opentelemetry.tracing._util.meta import (
    DtTraceState,
    get_fw4_tag,
    mark_propagated_now,
    set_fw4_tag,
)

# Use all-lowercase, see https://oaad.lab.dynatrace.org/shortlink/id-coreconcepts-taggingprotocols#opentelemetry-textmap-span-sensor
# The canonical spelling for HTTP would be X-dynaTrace, but we don't know which
# protocol we are actually injecting into/extracting from.
X_DYNATRACE_HEADER_KEY = "x-dynatrace"
X_DTC_HEADER_KEY = "x-dtc"


def _get_header(
    header_key: str, getter: Getter, carrier: CarrierT
) -> Optional[str]:
    header = getter.get(carrier, header_key)
    return header[0] if header else None


class DtTextMapPropagator(TextMapPropagator):
    """This class extracts and injects the Dynatrace FW4 tag from/into the
    headers of HTTP requests.

    A note on extraction/sampling: This implementation does not extract the
    W3C tracestate as-is in all cases.

    It implements some "sampling logic", to set the IS_SAMPLED traceparent flag
    according to the Dynatrace tag, or set it to true if there is none.
    """

    HTTP_TRACE_CONTEXT_FORMAT = TraceContextTextMapPropagator()

    def __init__(self, **kwargs):
        config = get_configuration(**kwargs)
        self._qualified_tenant_id = config.qualified_tenant_id
        self._rum_app_id = config.rum.application_id
        self._trace_state_key = get_trace_state_key(self._qualified_tenant_id)

    @property
    def fields(self) -> Set:
        header_fields = {X_DYNATRACE_HEADER_KEY, X_DTC_HEADER_KEY}
        header_fields.update(self.HTTP_TRACE_CONTEXT_FORMAT.fields)
        return header_fields

    ################################################################################
    # Inject
    ################################################################################

    def inject(
        self,
        carrier: CarrierT,
        context: Optional[Context] = None,
        setter: Setter = default_setter,
    ) -> None:
        span = get_current_span(context)
        span_context = span.get_span_context()
        if not span_context.is_valid:
            propagator_logger.debug("Invalid span, skipping tag injection")
            return

        mark_propagated_now(span)
        parent_tag = get_fw4_tag(span_context.trace_state)
        if not parent_tag:
            # usually there should already be a FW4 tag created by DtSpanProcessor
            # unsampled/NonRecordingSpan spans do not have a tag yet so create a new one
            parent_tag = Fw4Tag.create_tenant_root(self._qualified_tenant_id)

        tag = parent_tag.propagate(span_context)

        trace_state = span_context.trace_state.update(
            self._trace_state_key, to_trace_state_value(tag)
        )
        set_fw4_tag(trace_state, tag)
        inject_span_ctx = SpanContext(
            trace_id=span_context.trace_id,
            span_id=span_context.span_id,
            is_remote=span_context.is_remote,
            trace_state=trace_state,
            trace_flags=span_context.trace_flags,
        )
        context = set_span_in_context(
            NonRecordingSpan(inject_span_ctx), context
        )

        self.HTTP_TRACE_CONTEXT_FORMAT.inject(
            carrier, context=context, setter=setter
        )
        xdt_tag = to_x_dynatrace(tag)
        setter.set(carrier, X_DYNATRACE_HEADER_KEY, xdt_tag)

        propagator_logger.debug("Injected tag: %s", tag)

    ################################################################################
    # Extract
    ###############################################################################

    def extract(
        self,
        carrier: CarrierT,
        context: Optional[Context] = None,
        getter: Getter = default_getter,
    ) -> Context:
        if context is None:
            context = Context()

        extract_context = self._extract_trace_parent(getter, carrier, context)
        extracted_span = get_current_span(extract_context)

        span_context = INVALID_SPAN_CONTEXT
        if extracted_span is not get_current_span(context):
            span_context = extracted_span.get_span_context()

        # look for matching x-dynatrace FW4 tag first
        tag = self._extract_xdt_fw4_tag(getter, carrier)
        if tag:
            return self._span_from_xdt_fw4_tag(
                tag, span_context, extract_context
            )

        # look for matching FW4 tag in trace state next
        tag = self._extract_trace_state_fw4_tag(span_context)
        if tag:
            return self._span_from_trace_state_fw4_tag(
                tag, span_context, extract_context, context
            )

        # look for RUM tag next
        rum_tag = self._extract_rum_tag(getter, carrier)
        if rum_tag:
            return set_ctx_rum_tag(extract_context, rum_tag)

        # finally, valid spans are always sampled if there is no tag
        if span_context.is_valid:
            return self._extracted_span_from(
                span_context, extract_context, None
            )

        return extract_context

    # ------------------------------------------------------------------------------
    # Trace parent
    # ------------------------------------------------------------------------------

    def _extract_trace_parent(
        self,
        getter: Getter,
        carrier: CarrierT,
        context: Optional[Context],
    ) -> Context:
        try:
            return self.HTTP_TRACE_CONTEXT_FORMAT.extract(
                carrier, context=context, getter=getter
            )
        except ValueError:
            propagator_logger.info("Unparsable trace context", exc_info=True)
        except Exception:  # pylint:disable=broad-except
            propagator_logger.exception(
                "Unexpected error parsing trace context"
            )
        return context

    # ------------------------------------------------------------------------------
    # X-dynaTrace FW4 tag
    # ------------------------------------------------------------------------------

    def _extract_xdt_fw4_tag(
        self, getter: Getter, carrier: CarrierT
    ) -> Optional[Fw4Tag]:
        x_dynatrace_header = _get_header(
            X_DYNATRACE_HEADER_KEY, getter, carrier
        )
        if not x_dynatrace_header or x_dynatrace_header.startswith("MT"):
            # do not attempt to parse if it may be a mobile tag
            return None
        try:
            tag = parse_x_dynatrace(x_dynatrace_header)
            if self._is_xdt_tag_relevant(tag):
                return tag
        except ValueError:
            propagator_logger.info(
                "Unparsable x-dynatrace header", exc_info=True
            )
        except Exception:  # pylint:disable=broad-except
            propagator_logger.exception(
                "Unexpected error parsing x-dynatrace header"
            )
        return None

    def _is_xdt_tag_relevant(self, tag: Fw4Tag) -> bool:
        # only use tags which provide trace and span ID
        if not tag.has_trace_id or not tag.has_span_id:
            propagator_logger.debug(
                "Ignoring x-dynatrace tag without trace/span ID"
            )
            return False
        if tag.cluster_id != self._qualified_tenant_id.cluster_id:
            propagator_logger.debug(
                "ClusterId mismatch in x-dynatrace tag (%s != %s)",
                self._qualified_tenant_id.cluster_id,
                tag.cluster_id,
            )
            return False
        tenant_id = self._qualified_tenant_id.tenant_id
        if tag.tenant_id != tenant_id:
            propagator_logger.debug(
                "Tenant mismatch in x-dynatrace tag (%s != %s)",
                tenant_id,
                tag.tenant_id,
            )
            return False
        return True

    def _span_from_xdt_fw4_tag(
        self, tag: Fw4Tag, span_context: SpanContext, context: Context
    ) -> Context:
        propagator_logger.debug("Extracted x-dynatrace FW4 tag: %s", tag)
        if not span_context.is_valid or span_context.trace_id != tag.trace_id:
            if span_context.is_valid and span_context.trace_id != tag.trace_id:
                propagator_logger.debug(
                    "Trace ID mismatch: traceparent: %s, x-dynatrace: %s",
                    span_context.trace_id,
                    tag.trace_id,
                )
            trace_flags = (
                TraceFlags(TraceFlags.DEFAULT)
                if tag.is_ignored
                else TraceFlags(TraceFlags.SAMPLED)
            )
            span_context = SpanContext(
                trace_id=tag.trace_id,
                span_id=tag.span_id,
                is_remote=True,
                trace_state=DEFAULT_TRACE_STATE,  # is replaced later
                trace_flags=trace_flags,
            )

        return self._extracted_span_from(span_context, context, tag)

    # ------------------------------------------------------------------------------
    # Trace state FW4 tag
    # ------------------------------------------------------------------------------

    def _extract_trace_state_fw4_tag(
        self, span_context: SpanContext
    ) -> Optional[Fw4Tag]:
        if not span_context.is_valid:
            return None
        try:
            tag = from_trace_state(
                span_context.trace_state, self._qualified_tenant_id
            )
            return tag
        except ValueError:
            propagator_logger.info(
                "Unparsable tracestate at extract", exc_info=True
            )
        except Exception:  # pylint:disable=broad-except
            propagator_logger.exception(
                "Unexpected error parsing tracestate at extract"
            )
        return None

    def _span_from_trace_state_fw4_tag(
        self,
        tag: Fw4Tag,
        span_context: SpanContext,
        extracted_context: Context,
        orig_context: Context,
    ):
        propagator_logger.debug("Extracted tracestate FW4 tag: %s", tag)
        if tag.has_trace_id and tag.trace_id != span_context.trace_id:
            propagator_logger.warning(
                "Trace ID mismatch: traceparent: %s, tracestate: %s",
                span_context.trace_id,
                tag.trace_id,
            )
            return orig_context

        return self._extracted_span_from(
            span_context, extracted_context, tag, serialize_tag=False
        )

    # ------------------------------------------------------------------------------
    # RUM Tag
    # ------------------------------------------------------------------------------

    def _extract_rum_tag(
        self, getter: Getter, carrier: CarrierT
    ) -> Optional[RumTag]:
        mobile_tag = _get_header(X_DYNATRACE_HEADER_KEY, getter, carrier)
        rum_tag = RumTag.from_mobile_tag(mobile_tag)
        if rum_tag:
            propagator_logger.debug("Extracted mobile tag: %s", rum_tag)
            return rum_tag

        xdtc_header = _get_header(X_DTC_HEADER_KEY, getter, carrier)
        rum_tag = RumTag.from_xdtc_header(xdtc_header, self._rum_app_id)
        if rum_tag:
            propagator_logger.debug("Extracted x-dtc tag: %s", rum_tag)
            return rum_tag

        return None

    # ------------------------------------------------------------------------------
    # extracted span preparation
    # ------------------------------------------------------------------------------

    def _extracted_span_from(
        self,
        span_context: SpanContext,
        context: Context,
        tag: Optional[Fw4Tag],
        serialize_tag: bool = True,
    ) -> Context:
        # we do not sample spans only if tag is set to ignored, so update the
        # sampled flag to true even if no tag exists
        trace_flags = self._update_trace_flags(span_context, tag)
        trace_state = self._update_trace_state(
            span_context.trace_state, tag, serialize_tag
        )
        set_fw4_tag(trace_state, tag)

        span_context = SpanContext(
            span_context.trace_id,
            span_context.span_id,
            is_remote=span_context.is_remote,
            trace_state=trace_state,
            trace_flags=TraceFlags(trace_flags),
        )

        return set_span_in_context(NonRecordingSpan(span_context), context)

    def _update_trace_state(
        self,
        trace_state: TraceState,
        tag: Optional[Fw4Tag],
        serialize_tag: bool,
    ) -> TraceState:
        if tag and serialize_tag:
            updated_trace_state = trace_state.update(
                self._trace_state_key, to_trace_state_value(tag)
            )
            if updated_trace_state is trace_state:
                propagator_logger.warning("Could not update FW4 tag '%s'", tag)
            trace_state = updated_trace_state

        trace_state = DtTraceState(trace_state.items())
        trace_state.dt_fw4_tag = tag

        return trace_state

    @staticmethod
    def _update_trace_flags(
        span_context: SpanContext, tag: Optional[Fw4Tag]
    ) -> TraceFlags:
        # Override sampled bit with the one from Dynatrace
        # This should only be mismatching if a non-Dynatrace (or foreign tenant)
        # node was in-between.
        trace_flags = span_context.trace_flags
        if tag and tag.is_ignored:
            trace_flags &= ~TraceFlags.SAMPLED
        else:
            trace_flags |= TraceFlags.SAMPLED
        return trace_flags
