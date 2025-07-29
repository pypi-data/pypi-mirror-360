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

import abc
import enum
import typing

from dynatrace.opentelemetry.tracing._otel.api import (
    AttributeValue,
    format_span_id,
    format_trace_id,
)
from dynatrace.opentelemetry.tracing._otel.sdk import (
    ReadableSpan,
    SpanExportResult,
)
from dynatrace.opentelemetry.tracing._otel.time import _time_ns


class WatchedSpan:
    """Implements a watched span which supplements a :class:`sdk_trace.Span`

    This class provides transient data for a :class:`sdk_trace.Span` throughout
    multiple export runs (like the last time when the span was sent, the update
    sequence number, ...).
    """

    __slots__ = (
        "creation_time_nanos",
        "_span",
        "_end_time",
        "_update_seq_no",
        "_last_sent_nanos",
        "_propagated_resource_attrs",
    )

    def __init__(
        self,
        span: ReadableSpan,
        propagated_resource_attrs: typing.Dict[str, AttributeValue],
    ):
        self.creation_time_nanos = _time_ns()
        self._end_time = None
        self._update_seq_no = 0
        self._last_sent_nanos = 0
        self._span = span
        self._propagated_resource_attrs = propagated_resource_attrs

    def __repr__(self):
        span_context = self._span.get_span_context()
        return (
            f"{type(self).__name__}("
            f"trace_id=0x{format_trace_id(span_context.trace_id)}, "
            f"span_id=0x{format_span_id(span_context.span_id)})"
        )

    def is_older_than(self, time_in_nanos: int) -> bool:
        return self.creation_time_nanos < time_in_nanos

    @property
    def end_time(self):
        return self._end_time

    @property
    def has_ended(self):
        """Indicates if the SDK span was ended.

        This value will only be set at the beginning of an export run and will
        stay consistent throughout one export run. The value on the actual SDK
        span might change meanwhile, so the exporter must use this property and
        :func:`end_time` for consistency.
        """
        return self._end_time is not None

    @property
    def is_new(self):
        return self._update_seq_no == 0

    def update_end_time(self):
        """Updates the :func:`end_time` of this watched span from the given SDK
        span.

        This method should be called at the beginning of an export run and the
        :func:`end_time` of this watched span are to be used over the value in
        the SDK span.
        """
        self._end_time = self._span.end_time

    @property
    def update_seq_no(self) -> int:
        return self._update_seq_no

    def mark_buffered(self) -> None:
        """Marks the Span as buffered and increments the :func:`update_seq_no`."""
        self._last_sent_nanos = _time_ns()
        self._update_seq_no += 1

    @property
    def span(self) -> ReadableSpan:
        return self._span

    def get_nanos_since_last_send(self):
        return _time_ns() - self._last_sent_nanos

    @property
    def propagated_resource_attrs(self):
        return self._propagated_resource_attrs


class ExportKind(enum.Enum):
    """Specifies the kind of an export operation.

    Depending on the kind an exporter might consider different strategies in
    terms of connection timeouts and retry handling.
    """

    REGULAR = 1
    SHUTDOWN_OR_FLUSH = 2


SpanStream = typing.Iterable[WatchedSpan]


class WatchedSpanExporter(abc.ABC):
    """Interface for exporting watched spans."""

    @abc.abstractmethod
    def export(
        self, spans: SpanStream, export_kind: ExportKind
    ) -> SpanExportResult:
        """Exports a stream of Spans.

        Args:
            spans: The iterable of spans to be exported consisting of
                tuples of :class:`WatchedSpan` and :class:`sdk_trace.Span`.
                The exporter is responsible for splitting the iterable up into
                batches of appropriate size.
            export_kind: The kind of export determining connection timeouts and
                retry handling.

        Returns:
            The result of the export
        """

    def shutdown(self):
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
