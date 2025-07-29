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

from typing import (
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
)

import dynatrace.odin.semconv.v1 as semconv
from dynatrace.odin.proto.collector.common.v1 import (
    common_pb2 as collector_common_pb2,
)
from dynatrace.odin.proto.collector.trace.v1 import dt_span_export_pb2
from dynatrace.odin.proto.common.v1 import common_pb2
from dynatrace.odin.proto.resource.v1 import resource_pb2
from dynatrace.odin.proto.trace.v1 import trace_pb2
from dynatrace.opentelemetry.tracing import version
from dynatrace.opentelemetry.tracing._config.settings import EnvResources
from dynatrace.opentelemetry.tracing._export.span import (
    get_parent_span_context,
    get_tenant_parent_span_id,
)
from dynatrace.opentelemetry.tracing._export.types import (
    SpanStream,
    WatchedSpan,
)
from dynatrace.opentelemetry.tracing._logging.loggers import (
    serialization_logger,
)
from dynatrace.opentelemetry.tracing._otel.api import (
    Attributes,
    AttributeValue,
    Link,
    SpanContext,
    StatusCode,
)
from dynatrace.opentelemetry.tracing._otel.sdk import (
    Event,
    ReadableSpan,
    Resource,
)
from dynatrace.opentelemetry.tracing._propagator.tags import Fw4Tag
from dynatrace.opentelemetry.tracing._util.meta import (
    _SPAN_ATTR_KEY_LAST_PROP_TIME,
    _SPAN_ATTR_KEY_MOBILE_TAG,
    get_fw4_tag,
    get_last_propagation_time_nanos,
    get_mobile_tag,
)
from dynatrace.opentelemetry.tracing._util.tenant import QualifiedTenantId

# https://github.com/open-telemetry/opentelemetry-java/blob/v0.3.0/api/src/main/java/io/opentelemetry/trace/SpanId.java#L121-L123
_IDENTIFIER_BYTE_ORDER = "big"


class SpanGroupKey(NamedTuple):
    server_id: int
    path_info: int
    trace_id: int


class SpanGroup(NamedTuple):
    trace_id_serialized: bytes
    parent_custom_tag: Optional[trace_pb2.CustomTag]
    spans_serialized: List[trace_pb2.Span]


# attribute type aliases
STRING_TYPE = common_pb2.AttributeKeyValue.ValueType.STRING
STRING_ARRAY_TYPE = common_pb2.AttributeKeyValue.ValueType.STRING_ARRAY
INT_TYPE = common_pb2.AttributeKeyValue.ValueType.INT
INT_ARRAY_TYPE = common_pb2.AttributeKeyValue.ValueType.INT_ARRAY
DOUBLE_TYPE = common_pb2.AttributeKeyValue.ValueType.DOUBLE
DOUBLE_ARRAY_TYPE = common_pb2.AttributeKeyValue.ValueType.DOUBLE_ARRAY
BOOL_TYPE = common_pb2.AttributeKeyValue.ValueType.BOOL
BOOL_ARRAY_TYPE = common_pb2.AttributeKeyValue.ValueType.BOOL_ARRAY
VALUELESS_ARRAY_TYPE = common_pb2.AttributeKeyValue.ValueType.VALUELESS_ARRAY

STATUS_CODE_MAPPING = {
    StatusCode.OK: trace_pb2.Status.Ok,
    StatusCode.UNSET: trace_pb2.Status.Ok,
    StatusCode.ERROR: trace_pb2.Status.UnknownError,
}

_EXCLUDED_ATTRIBUTES = {
    _SPAN_ATTR_KEY_MOBILE_TAG,
    _SPAN_ATTR_KEY_LAST_PROP_TIME,
}


def _get_trace_id_from(span_context: SpanContext) -> bytes:
    return span_context.trace_id.to_bytes(128 // 8, _IDENTIFIER_BYTE_ORDER)


def _span_id_to_bytes(span_id: int) -> bytes:
    return span_id.to_bytes(64 // 8, _IDENTIFIER_BYTE_ORDER)


def _get_span_id_from(span_context: SpanContext) -> bytes:
    return _span_id_to_bytes(span_context.span_id)


def _create_attribute(
    pb_attributes, key: str, attr_type: common_pb2.AttributeKeyValue.ValueType
) -> common_pb2.AttributeKeyValue:
    attribute = pb_attributes.add()
    attribute.key = key
    attribute.type = attr_type
    return attribute


def _add_pb_attr(pb_attributes, key: str, value: AttributeValue):
    """Adds a protobuf attribute for the given value to the given protobuf
    attributes container.

    This method will check the type of the given input value and set
    corresponding type and value on the added protobuf object.

    Args:
        pb_attributes: the protobuf container to which the corresponding
            protobuf object will be added.
        value: the value to be set on the added protobuf object
    """
    if isinstance(value, str):
        attribute = _create_attribute(pb_attributes, key, STRING_TYPE)
        attribute.string_value = value
        return
    if isinstance(value, bool):
        attribute = _create_attribute(pb_attributes, key, BOOL_TYPE)
        attribute.bool_value = value
        return
    if isinstance(value, int):
        attribute = _create_attribute(pb_attributes, key, INT_TYPE)
        attribute.int_value = value
        return
    if isinstance(value, float):
        attribute = _create_attribute(pb_attributes, key, DOUBLE_TYPE)
        attribute.double_value = value
        return
    if isinstance(value, Sequence):
        _add_array_attribute(pb_attributes, key, value)
        return

    serialization_logger.warning(
        "Skipped attribute '%s' because of unsupported type %s",
        key,
        type(value),
    )


def _add_array_attribute(pb_attributes, key: str, value: Sequence):
    array_attr_type = _determine_array_attribute_type(value)
    if array_attr_type is None:
        _create_attribute(pb_attributes, key, VALUELESS_ARRAY_TYPE)
        return

    if issubclass(array_attr_type, str):
        attribute = _create_attribute(pb_attributes, key, STRING_ARRAY_TYPE)
        attr_array = attribute.string_values
        default_value = ""
    elif issubclass(array_attr_type, bool):
        attribute = _create_attribute(pb_attributes, key, BOOL_ARRAY_TYPE)
        attr_array = attribute.bool_values
        default_value = False
    elif issubclass(array_attr_type, int):
        attribute = _create_attribute(pb_attributes, key, INT_ARRAY_TYPE)
        attr_array = attribute.int_values
        default_value = 0
    elif issubclass(array_attr_type, float):
        attribute = _create_attribute(pb_attributes, key, DOUBLE_ARRAY_TYPE)
        attr_array = attribute.double_values
        default_value = 0.0
    else:
        serialization_logger.warning(
            "Skipped array attribute '%s' because of unsupported type %s",
            key,
            array_attr_type,
        )
        return

    for array_elem in value:
        if array_elem is None:
            array_elem = default_value  # default value
        attr_array.append(array_elem)


def _determine_array_attribute_type(array_value: Sequence) -> Optional[Type]:
    first_type = None
    for value in array_value:
        if value is None:
            continue
        first_type = type(value)
        break
    return first_type


def _add_pb_attrs(attribute_dict: Attributes, pb_attributes):
    """Adds a protobuf attribute for each value in the given dictionary.

    Will iterate over each entry in the given dictionary and try to add a
    corresponding protobuf attribute to the given protobuf container. Values
    of unknown types skipped and logged accordingly.

    Args:
        attribute_dict: the input dictionary from which the corresponding
            protobuf attributes will be created.
        pb_attributes: the protobuf container into which the newly
            created protobuf attribute will be added.
    """
    if attribute_dict is None:
        return

    for key, value in attribute_dict.items():
        if key in _EXCLUDED_ATTRIBUTES:
            continue
        _add_pb_attr(pb_attributes, key, value)


def _add_instrumentation_scope(span: ReadableSpan, pb_attributes):
    attribute = _create_attribute(
        pb_attributes, semconv.OTEL_LIBRARY_NAME, STRING_TYPE
    )
    scope = getattr(span, "instrumentation_scope", None)
    if scope is None:
        scope = span.instrumentation_info

    attribute.string_value = scope.name

    if scope.version:
        attribute = _create_attribute(
            pb_attributes, semconv.OTEL_LIBRARY_VERSION, STRING_TYPE
        )
        attribute.string_value = scope.version


def _store_link_in_protobuf(link: Link, pb_link: trace_pb2.Span.Link) -> None:
    """Sets all relevant fields of the given :class:`Link` to the
    given protobuf object.

    Args:
        link: The :class:`Link` which's fields will be converted
            and set onto the given protobuf link object.
        pb_link: The protobuf link onto which the converted fields of
            the given link will be applied.
    """
    link_context = link.context
    pb_link.trace_id = _get_trace_id_from(link_context)
    pb_link.span_id = _get_span_id_from(link_context)

    if link_context.is_remote:
        fw4_tag = get_fw4_tag(link_context.trace_state)
        if fw4_tag:
            pb_link.fwtag_encoded_link_id = fw4_tag.encoded_link_id

    _add_pb_attrs(link.attributes, pb_link.attributes)


def _store_event_in_protobuf(
    event: Event, pb_event: trace_pb2.Span.Event
) -> None:
    """Sets the relevant fields from the given :class:`sdk_trace.Event`
    onto the given protobuf object.

    Args:
        event: The :class:`sdk_trace.Event` which's fields will be
            converted and set onto given protobuf event object.
        pb_event: The protobuf event onto which the converted fields
            of the given event will be applied.
    """
    pb_event.time_unixnano = event.timestamp
    pb_event.name = event.name

    _add_pb_attrs(event.attributes, pb_event.attributes)


def _store_span_in_protobuf(
    watched_span: WatchedSpan,
    trace_id: bytes,
    pb_span: trace_pb2.Span,
    tag: Optional[Fw4Tag],
) -> None:
    """Sets all relevant fields of the given :class:`WatchedSpan` in
    the given :class:`pb2_trace.Span` object.

    This function will subsequently also convert all events and links.

    Args:
        watched_span: The :class:`dt_trace.WatchedSpan` which manages
            transient and provides additional data to the given sdk_span.
        trace_id: The identifier of the trace to which the given span
            belongs to. This trace_id could be obtained from the given span but
            is explicitly passed here to avoid converting it twice.
        pb_span: The protobuf span object onto which the relevant
            fields will be written to.
    """
    span = watched_span.span
    pb_span.trace_id = trace_id
    pb_span.span_id = _get_span_id_from(span.context)
    pb_span.update_sequence_no = watched_span.update_seq_no

    if not watched_span.has_ended and not watched_span.is_new:
        pb_span.send_reason = trace_pb2.Span.SendReason.KeepAlive
        return

    pb_span.send_reason = (
        trace_pb2.Span.SendReason.Ended
        if watched_span.has_ended
        else trace_pb2.Span.SendReason.NewOrChanged
    )

    pb_span.name = span.name
    pb_span.kind = getattr(trace_pb2.Span.SpanKind, span.kind.name)

    if span.status is not None:
        pb_span.status.code = STATUS_CODE_MAPPING.get(
            span.status.status_code, trace_pb2.Status.Ok
        )
        if span.status.description is not None:
            pb_span.status.message = span.status.description

    _set_pb_span_parent_data(pb_span, span, tag)
    _set_span_metadata(pb_span, span)

    pb_span.start_time_unixnano = span.start_time
    if watched_span.has_ended:
        pb_span.end_time_unixnano = watched_span.end_time

    _add_instrumentation_scope(span, pb_span.attributes)
    _add_pb_attrs(_get_span_attributes(watched_span), pb_span.attributes)

    for event in span.events:
        pb_event = pb_span.events.add()
        _store_event_in_protobuf(event, pb_event)

    for link in span.links:
        pb_link = pb_span.links.add()
        _store_link_in_protobuf(link, pb_link)


def _get_span_attributes(watched_span: WatchedSpan) -> Attributes:
    span = watched_span.span

    if not watched_span.propagated_resource_attrs:
        return span.attributes

    attrs = watched_span.propagated_resource_attrs.copy()
    for key, value in span.attributes.items():
        propagated_value = attrs.get(key, None)
        if propagated_value is not None and propagated_value != value:
            # since we support at most 1 overwritten attribute per key here
            # we can hardcode the prefix to index 1
            key = f"overwritten1.{key}"
        attrs[key] = value

    return attrs


def _set_span_metadata(pb_span: trace_pb2.Span, span: ReadableSpan):
    last_prop_time_ns = get_last_propagation_time_nanos(span)
    if last_prop_time_ns is not None:
        pb_span.last_propagate_time_unixnano = last_prop_time_ns

    mobile_tag = get_mobile_tag(span)
    if mobile_tag:
        pb_span.mobile_tag = mobile_tag


def _set_pb_span_parent_data(
    pb_span: trace_pb2.Span, span: ReadableSpan, tag: Optional[Fw4Tag]
):
    parent_context = get_parent_span_context(span)
    if not parent_context.is_valid:
        return

    pb_span.parent_span_id = _get_span_id_from(parent_context)
    tenant_parent_id = get_tenant_parent_span_id(parent_context, tag)
    if tenant_parent_id is not None:
        pb_span.tenant_parent_span_id = _span_id_to_bytes(tenant_parent_id)

    if parent_context.is_remote and tag:
        pb_span.parent_fwtag_encoded_link_id = tag.encoded_link_id


def _prepare_envelopes(
    span_group_key: SpanGroupKey, span_group: SpanGroup
) -> Tuple[
    dt_span_export_pb2.ActiveGateSpanEnvelope,
    dt_span_export_pb2.ClusterSpanEnvelope,
    int,  # Estimated size
]:
    """Creates an active gate and a cluster envelope protobuf object containing
    all spans provided in the given group info.

    Args:
        span_group_key: The key on which the spans were pre-grouped
        span_group: An object providing the pre-grouped spans.
    """
    cluster_envelope = dt_span_export_pb2.ClusterSpanEnvelope()
    cluster_envelope.traceId = span_group.trace_id_serialized
    cluster_envelope.pathInfo = span_group_key.path_info
    if span_group.parent_custom_tag is not None:
        cluster_envelope.customTags.append(span_group.parent_custom_tag)

    # Estimate 1 byte for the tag size and up to 4 byte for the varint
    # encoding the size of the span container.
    estimated_size = cluster_envelope.ByteSize() + 1 + 4

    ag_envelope = dt_span_export_pb2.ActiveGateSpanEnvelope()
    if span_group_key.server_id != 0:
        ag_envelope.serverId = span_group_key.server_id
    else:
        ag_envelope.traceId = span_group.trace_id_serialized

    # Estimate 1 byte for the tag size and up to 4 byte for the varint
    # encoding the size of the cluster envelope.
    estimated_size += ag_envelope.ByteSize() + 1 + 4

    # log before gluing all together to avoid serialized byte strings in output
    serialization_logger.debug(
        "Prepared ClusterSpanEnvelope(%s) in ActiveGateSpanEnvelope(%s)",
        cluster_envelope,
        ag_envelope,
    )
    return ag_envelope, cluster_envelope, estimated_size


def _serialize_resource_and_meta_info(
    span_export: dt_span_export_pb2.SpanExport,
    resource: Resource,
    env_resources: EnvResources,
):
    pb_resource = _create_pb_resource_from(resource, env_resources)

    meta_info = collector_common_pb2.ExportMetaInfo()
    meta_info.timeSyncMode = (
        collector_common_pb2.ExportMetaInfo.TimeSyncMode.NTPSync
    )
    meta_info.clusterTimeOffsetMs = 0

    serialization_logger.debug(
        "Serializing ExportMetaInfo(%s), Resource(%s)", meta_info, pb_resource
    )

    span_export.resource = pb_resource.SerializeToString()
    span_export.exportMetaInfo = meta_info.SerializeToString()


def _create_pb_resource_from(
    resource: Resource, env_resources: EnvResources
) -> resource_pb2.Resource:
    pb_resource = resource_pb2.Resource()
    attrs = pb_resource.attributes

    _add_pb_attrs(resource.attributes, attrs)
    _add_pb_attr(attrs, semconv.TELEMETRY_EXPORTER_NAME, "odin")
    _add_pb_attr(
        attrs, semconv.TELEMETRY_EXPORTER_VERSION, version.FULL_VERSION
    )
    if version.IS_PACKAGE_MODE:
        _add_pb_attr(
            attrs,
            semconv.TELEMETRY_EXPORTER_PACKAGE_VERSION,
            version.__version__,
        )

    if env_resources.tags:
        _add_pb_attr(attrs, semconv.DT_ENV_VARS_DT_TAGS, env_resources.tags)
    if env_resources.custom_prop:
        _add_pb_attr(
            attrs,
            semconv.DT_ENV_VARS_DT_CUSTOM_PROP,
            env_resources.custom_prop,
        )

    return pb_resource


def _assert_resource(
    reference_resource: Resource, span: ReadableSpan
) -> Resource:
    span_resource = span.resource
    if span_resource is None:
        raise ValueError("Bad span: No resource.")
    if reference_resource is None:
        return span_resource
    if reference_resource is not span_resource:
        raise ValueError("Span resource mismatch.")

    return reference_resource


def _create_custom_tag_protobuf(
    tag: Optional[Fw4Tag],
) -> Optional[trace_pb2.CustomTag]:
    if not tag or not tag.custom_blob:
        return None
    custom_tag = trace_pb2.CustomTag()
    # there is only propagation of incoming custom tags, we do not create
    # outgoing custom tags
    custom_tag.direction = trace_pb2.CustomTag.Direction.Incoming
    custom_tag.type = tag.custom_blob[0]  # first byte in blob defines the type
    custom_tag.tagValue = tag.custom_blob[1:]  # the rest is the value
    return custom_tag


def _get_span_group(
    span_groups: Dict[SpanGroupKey, SpanGroup],
    span_context: SpanContext,
    tag: Optional[Fw4Tag],
) -> SpanGroup:
    if tag:
        server_id = tag.server_id
        path_info = tag.path_info
    else:
        serialization_logger.error("Span without fw4 tag: %s", span_context)
        server_id = 0
        path_info = 0

    key = SpanGroupKey(
        server_id=server_id,
        path_info=path_info,
        trace_id=span_context.trace_id,
    )
    span_group = span_groups.get(key, None)
    if span_group is None:
        span_group = SpanGroup(
            trace_id_serialized=_get_trace_id_from(span_context),
            parent_custom_tag=_create_custom_tag_protobuf(tag),
            spans_serialized=[],
        )
        span_groups[key] = span_group

    return span_group


def _group_spans(
    spans: SpanStream,
) -> Tuple[Resource, Dict[SpanGroupKey, SpanGroup]]:
    reference_resource = None
    span_groups = {}
    for watched_span in spans:
        sdk_span = watched_span.span
        reference_resource = _assert_resource(reference_resource, sdk_span)

        span_context = sdk_span.context
        tag = get_fw4_tag(span_context.trace_state)
        group = _get_span_group(span_groups, span_context, tag)

        pb_span = trace_pb2.Span()
        _store_span_in_protobuf(
            watched_span, group.trace_id_serialized, pb_span, tag
        )
        group.spans_serialized.append(pb_span)
        watched_span.mark_buffered()
    return reference_resource, span_groups


def serialize_for_export(
    spans: SpanStream,
    qualified_tenant_id: QualifiedTenantId,
    exporter_id: int,
    env_resources: EnvResources,
    desired_size: int,
    max_size: int,
) -> Iterable[dt_span_export_pb2.SpanExport]:
    """Serializes the given sequence of spans into corresponding span
    export objects.

    Args:
        spans: A sequence of :class:`dt_trace.WatchedSpan` which are to be
            serialized to a span export message.
        qualified_tenant_id: The identifier of the tenant for which to report
            spans
        exporter_id: The identifier of the exporter which is sending the spans.
    Returns:
        The spans in serialized representations ready for export. The iterator
        will yield the same object instance each time, so make sure to copy the
        protobuf object if you need to use it later.
    """

    # pylint:disable=too-many-locals

    export_data = dt_span_export_pb2.SpanExport()

    export_data.tenantUUID = qualified_tenant_id.tenant_uuid
    export_data.agentId = exporter_id

    serialization_logger.debug("Serializing SpanExport(%s)", export_data)

    # TODO sort the spans by (server_id, trace_id) and do grouping with a list
    # of SpanGroupInfo by iterating over the sorted spans. Requires that the
    # tag is patched on the parent's span_context to avoid multiple tag parsings
    reference_resource, span_groups = _group_spans(spans)

    if not span_groups:
        return

    _serialize_resource_and_meta_info(
        export_data, reference_resource, env_resources
    )
    spanless_message_size = export_data.ByteSize()
    if spanless_message_size >= max_size:
        raise ValueError(
            f"Resource too big ({spanless_message_size} B, max={max_size} B) "
            "-- cannot export any spans"
        )

    export_has_span = False

    size_so_far = spanless_message_size

    for key, group in span_groups.items():
        ag_envelope, cluster_envelope, envelope_size = _prepare_envelopes(
            key, group
        )
        size_so_far += envelope_size
        span_container = dt_span_export_pb2.SpanContainer()

        def finish_envelopes():
            # Var usage is OK here since we only call this function instance in
            # this loop iteration.
            # pylint:disable=cell-var-from-loop

            if not span_container.spans:
                return

            serialization_logger.debug("Serializing Spans(%s)", span_container)

            cluster_envelope.spanContainer = span_container.SerializeToString()
            ag_envelope.clusterSpanEnvelope = (
                cluster_envelope.SerializeToString()
            )
            export_data.spans.append(ag_envelope)

        for span in group.spans_serialized:
            # Estimate 1 byte for the tag size in the container + 4 for size prefix
            next_size = span.ByteSize() + 1 + 4
            if size_so_far + next_size > desired_size:
                min_size = spanless_message_size + envelope_size + next_size
                if min_size > max_size:
                    serialization_logger.error(
                        "Dropped span, %s bytes would be too large to send (max=%s)",
                        min_size,
                        max_size,
                    )
                    continue
                if export_has_span:
                    finish_envelopes()
                    yield export_data
                    del span_container.spans[:]
                    size_so_far = spanless_message_size + envelope_size
                    export_has_span = False
                    del export_data.spans[:]
            span_container.spans.append(span)
            size_so_far += next_size
            export_has_span = True
        finish_envelopes()

    if export_data.spans:
        yield export_data
