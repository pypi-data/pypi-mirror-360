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

from typing import Callable, Optional

from dynatrace.opentelemetry.tracing._logging.loggers import core_logger
from dynatrace.opentelemetry.tracing._otel.api import Span, TraceState
from dynatrace.opentelemetry.tracing._otel.sdk import ReadableSpan
from dynatrace.opentelemetry.tracing._otel.time import _time_ns
from dynatrace.opentelemetry.tracing._propagator.tags import Fw4Tag

_SPAN_METADATA_KEY = "_dt_span_metadata"

_SPAN_ATTR_KEY_LAST_PROP_TIME = "dt.__last_propagation_time"
_SPAN_ATTR_KEY_MOBILE_TAG = "dt.__mobiletag.in"

################################################################################
# TraceState
################################################################################


class DtTraceState(TraceState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dt_fw4_tag = None  # type: Optional[Fw4Tag]

    def add(self, key: str, value: str) -> "DtTraceState":
        return self._as_dt_trace_state(super().add, key, value)

    def update(self, key: str, value: str) -> "DtTraceState":
        return self._as_dt_trace_state(super().update, key, value)

    def delete(self, key: str) -> "DtTraceState":
        return self._as_dt_trace_state(super().delete, key)

    def _as_dt_trace_state(
        self, func: Callable, *args, **kwargs
    ) -> "DtTraceState":
        trace_state = func(*args, **kwargs)

        dt_trace_state = DtTraceState(trace_state.items())
        dt_trace_state.dt_fw4_tag = self.dt_fw4_tag
        return dt_trace_state


def get_fw4_tag(trace_state: TraceState) -> Optional[Fw4Tag]:
    if isinstance(trace_state, DtTraceState):
        return trace_state.dt_fw4_tag

    return None


def set_fw4_tag(trace_state: TraceState, tag: Fw4Tag):
    if isinstance(trace_state, DtTraceState):
        trace_state.dt_fw4_tag = tag
    else:
        core_logger.warning(
            "Cannot set FW4 tag '%s' because trace state "
            "is not of type 'DtTraceState'",
            tag,
        )


################################################################################
# Span meta data
################################################################################


def mark_propagated_now(span: Span):
    if span.is_recording():
        span.set_attribute(_SPAN_ATTR_KEY_LAST_PROP_TIME, _time_ns())


def get_last_propagation_time_nanos(span: ReadableSpan) -> int:
    return span.attributes.get(_SPAN_ATTR_KEY_LAST_PROP_TIME) or 0


def set_mobile_tag(span: Span, mobile_tag: str):
    if not mobile_tag:
        return
    span.set_attribute(_SPAN_ATTR_KEY_MOBILE_TAG, mobile_tag)


def get_mobile_tag(span: ReadableSpan) -> Optional[str]:
    return span.attributes.get(_SPAN_ATTR_KEY_MOBILE_TAG)
