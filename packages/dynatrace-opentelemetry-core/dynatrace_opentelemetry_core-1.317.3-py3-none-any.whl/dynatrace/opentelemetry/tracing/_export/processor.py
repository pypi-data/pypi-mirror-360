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

import os
import threading
import traceback
from typing import List, Optional

from dynatrace.odin.semconv import v1 as semconv
from dynatrace.opentelemetry.tracing._config.reader import get_configuration
from dynatrace.opentelemetry.tracing._export.exporter import DtSpanExporter
from dynatrace.opentelemetry.tracing._export.types import (
    ExportKind,
    SpanStream,
    WatchedSpan,
    WatchedSpanExporter,
)
from dynatrace.opentelemetry.tracing._logging.loggers import processor_logger
from dynatrace.opentelemetry.tracing._otel.api import Context, get_current_span
from dynatrace.opentelemetry.tracing._otel.sdk import (
    ReadableSpan,
    Span,
    SpanProcessor,
)
from dynatrace.opentelemetry.tracing._otel.time import _time_ns
from dynatrace.opentelemetry.tracing._propagator.tags import Fw4Tag
from dynatrace.opentelemetry.tracing._util import meta
from dynatrace.opentelemetry.tracing._util.context import (
    get_ctx_rum_tag,
    get_propagated_resource_attributes,
    suppressed_tracing,
)


class DtSpanProcessor(SpanProcessor):
    """Implementation of a span processor that repeatedly reports active spans.

    Spans processed by this span processor are maintained in a watchlist and get
    exported periodically in batches. Spans are removed from the watchlist once
    they are ended or their maximum age is exceeded.

    The size of the watchlist is limited to a pre-defined number of spans. Once
    this number is exceeded new spans are dropped until space becomes available
    again (i.e. a span in the watchlist is ended or exceeds the maximum age)
    """

    def __init__(self, **kwargs):
        exporter = kwargs.pop("exporter", None)
        config = get_configuration(**kwargs)

        if exporter is None:
            exporter = DtSpanExporter(config=config)
        if not isinstance(exporter, WatchedSpanExporter):
            raise ValueError("exporter must be an instance of DtSpanExporter")

        if config.extra.max_watchlist_size <= 0:
            raise ValueError("max_watchlist_size must be a positive integer.")

        if config.extra.report_interval_millis < 0:
            raise ValueError("report_interval_millis must not be negative.")

        if config.extra.keep_alive_interval_millis < 0:
            raise ValueError(
                "keep_alive_interval_millis must not be negative."
            )
        self._keep_alive_interval_millis = (
            config.extra.keep_alive_interval_millis
        )

        self._qualified_tenant_id = config.qualified_tenant_id
        self._exporter = exporter

        self._report_interval_millis = config.extra.report_interval_millis
        self._max_watchlist_size = config.extra.max_watchlist_size

        self._max_span_age_nanos = config.extra.max_span_age_millis * 1000000

        self._shutdown_or_flush_timeout_millis = (
            config.connection.flush_connect_timeout_millis
            + config.connection.flush_data_timeout_millis
        )

        self._done = False
        # flag that indicates that spans have been dropped
        self._spans_dropped = False

        # Would be nice to handle this in a separate span processor, but since we expose
        # this one in the API and want this flag to still work w/o code changes, so be it.
        self._add_stack_on_start = config.debug.add_stack_on_start

        # re-initializable attributes
        self._condition = None
        self._span_watchlist = None
        self._span_watchlist_size = 0
        self._approx_pending_ended_span_count = 0
        self._fresh_spans = None
        self._watched_span_lookup = None
        self._flush_request = None  # type: Optional[threading.Event]
        self._pid = None
        self._initialize_export_worker()

        if hasattr(os, "register_at_fork"):
            os.register_at_fork(after_in_child=self._initialize_export_worker)

    def _initialize_export_worker(self):
        self._condition = threading.Condition()
        # The active spans which this span processor is keeping track of.
        self._span_watchlist = []
        self._span_watchlist_size = 0
        # Tracks the number of ended spans since last export. Might be higher
        # than the actual number of ended spans since ended spans are still
        # picked up while the exporter is running.
        self._approx_pending_ended_span_count = 0
        #  A list of freshly added spans which will be taken over to the
        # span watchlist on every export run.
        self._fresh_spans = []
        self._watched_span_lookup = _WatchedSpanLookup()
        self._flush_request = None
        self._pid = os.getpid()

        self._worker_thread = threading.Thread(
            target=self._worker, name="DtSpanProcessor", daemon=True
        )
        self._start_worker()

    def _start_worker(self):
        self._worker_thread.start()

    def _get_current_watchlist_size(self) -> int:
        return len(self._fresh_spans) + self._span_watchlist_size

    def _can_add_span(self) -> bool:
        return self._get_current_watchlist_size() < self._max_watchlist_size

    @staticmethod
    def _can_process_span(span: ReadableSpan) -> bool:
        trace_state = span.get_span_context().trace_state
        return isinstance(trace_state, meta.DtTraceState)

    def on_start(self, span: Span, parent_context: Optional[Context] = None):
        if self._done:
            processor_logger.warning(
                "Already shut down, ignoring on_start for %s.", span
            )
            return

        if not self._can_process_span(span):
            processor_logger.warning(
                "Cannot process '%s' because trace state is not of type "
                "'DtTraceState'. 'DtSampler' not in use?",
                span,
            )
            return

        self._prepare_span(span, parent_context)

        propagated_attrs = get_propagated_resource_attributes(parent_context)
        watched_span = WatchedSpan(span, propagated_attrs)
        with self._condition:
            if not self._can_add_span():
                processor_logger.debug(
                    "Could not add new %s, watchlist full", watched_span
                )
                return

            watched_span = self._watched_span_lookup.add(watched_span)
            self._fresh_spans.append(watched_span)

    def _prepare_span(self, span: Span, context: Optional[Context]):
        if self._add_stack_on_start:
            stack = "".join(traceback.format_stack())
            processor_logger.debug(
                "%s=%s", semconv.DT_STACKTRACE_ONSTART, stack
            )
            span.set_attribute(semconv.DT_STACKTRACE_ONSTART, stack)

        span_context = span.get_span_context()

        # for child spans update the last propagation time on parent
        parent_span = get_current_span(context)
        meta.mark_propagated_now(parent_span)

        fw4_tag = meta.get_fw4_tag(span_context.trace_state)
        if fw4_tag:
            # nothing to do when we already have a tag extracted by the propagator
            return

        # create a new FW4 tag for local spans or for remote spans which did not
        # yet have an FW4 tag for the tenant
        fw4_tag = Fw4Tag.create_tenant_root(self._qualified_tenant_id)
        meta.set_fw4_tag(span_context.trace_state, fw4_tag)

        rum_tag = get_ctx_rum_tag(context)
        if rum_tag is None:
            return

        fw4_tag.server_id = rum_tag.server_id
        meta.set_mobile_tag(span, rum_tag.mobile_tag)

        if rum_tag.xdtc_header:
            span.set_attribute(semconv.DT_RUM_DTC, rum_tag.xdtc_header)
            if rum_tag.rum_app_id:
                span.set_attribute(
                    semconv.DT_RUM_APP_ME_ID, rum_tag.rum_app_id
                )

    def on_end(self, span: ReadableSpan):
        if self._done:
            processor_logger.warning(
                "Already shut down, ignoring on_end for %s.", span
            )
            return

        self._record_ended_span(span)

        with self._condition:
            # notify worker/exporter if sufficient ended spans available
            if (
                self._get_current_watchlist_size()
                >= self._max_watchlist_size // 2
                and self._approx_pending_ended_span_count > 0
                and self._approx_pending_ended_span_count
                >= self._max_watchlist_size // 5
            ):
                self._condition.notify_all()

    def _record_ended_span(self, span: ReadableSpan):
        if not self._can_process_span(span):
            return

        with self._condition:
            watched_span = self._watched_span_lookup.remove(span)
            if watched_span is None:
                # most likely span watchlist was full on start, ignore
                processor_logger.debug(
                    "Ignoring ended %s not found in watchlist",
                    WatchedSpan(span, {}),
                )
                return

            self._approx_pending_ended_span_count += 1

    def _worker(self):
        flush_request = None  # type: Optional[threading.Event]
        while not self._done:
            with self._condition:
                if self._done:
                    # done flag might have changed, avoid waiting
                    break
                flush_request = self._get_and_unset_flush_request()
                # skip waiting on flush request. otherwise the flush initiator
                # will time out unless someone else notifies _condition
                if flush_request is None:
                    self._condition.wait(self._report_interval_millis / 1e3)
                    flush_request = self._get_and_unset_flush_request()

                if not self._span_watchlist and not self._fresh_spans:
                    # spurious notification, let's wait again
                    self._notify_flush_request_finished(flush_request)
                    flush_request = None
                    continue
                if self._done:
                    # missing spans will be sent when calling flush
                    break
                self._pump_fresh_spans()

            export_kind = self._get_export_kind(flush_request)
            self._export(self._span_watchlist, export_kind)

            with self._condition:
                self._span_watchlist_size = len(self._span_watchlist)
            self._notify_flush_request_finished(flush_request)
            flush_request = None

        # there might have been a new flush request while export was running
        # and before the done flag switched to true
        with self._condition:
            shutdown_flush_request = self._get_and_unset_flush_request()

        # be sure that all spans are sent
        self._export_remaining_spans()
        self._notify_flush_request_finished(flush_request)
        self._notify_flush_request_finished(shutdown_flush_request)

    @staticmethod
    def _get_export_kind(
        flush_request: Optional[threading.Event],
    ) -> ExportKind:
        return (
            ExportKind.REGULAR
            if flush_request is None
            else ExportKind.SHUTDOWN_OR_FLUSH
        )

    def _get_and_unset_flush_request(self) -> Optional[threading.Event]:
        """Returns the current flush request and makes it invisible to the
        worker thread for subsequent calls.
        """
        flush_request = self._flush_request
        self._flush_request = None
        return flush_request

    @staticmethod
    def _notify_flush_request_finished(
        flush_request: Optional[threading.Event],
    ):
        """Notifies the flush initiator(s) waiting on the given request/event
        that the flush operation was finished.
        """
        if flush_request is not None:
            flush_request.set()

    def _get_or_create_flush_request(self) -> threading.Event:
        """Either returns the current active flush event or creates a new one.

        The flush event will be visible and read by the worker thread before an
        export operation starts. Callers of a flush operation may wait on the
        returned event to be notified when the flush/export operation was
        finished.

        This method is not thread-safe, i.e. callers need to take care about
        synchronization/locking.
        """
        if self._flush_request is None:
            self._flush_request = threading.Event()
        return self._flush_request

    def _pump_fresh_spans(self):
        assert self._span_watchlist_size == len(self._span_watchlist)
        self._span_watchlist += self._fresh_spans
        self._fresh_spans.clear()

        self._span_watchlist_size = len(self._span_watchlist)
        self._approx_pending_ended_span_count = 0

    def _export_batch(
        self, spans: SpanStream, export_kind: ExportKind
    ) -> None:
        with suppressed_tracing():
            try:
                self._exporter.export(spans, export_kind)
            except Exception:  # pylint:disable=broad-except
                processor_logger.exception(
                    "Failed exporting active span batch."
                )

    def _should_report_span(self, watched_span: WatchedSpan) -> bool:
        if watched_span.has_ended:
            return True

        # report spans only if they are new or when it is time to send the
        # next keep alive message
        return (
            watched_span.is_new
            or watched_span.get_nanos_since_last_send() / 1e6
            + self._report_interval_millis
            >= self._keep_alive_interval_millis
        )

    def _collect_spans_for_export(
        self,
        watchlist: List[WatchedSpan],
        one_interval_ago_nanos: int,
        min_creation_time_nanos: int,
    ) -> SpanStream:
        index = 0
        while index < len(watchlist):
            watched_span = watchlist[index]

            if watched_span.is_older_than(min_creation_time_nanos):
                self._watched_span_lookup.remove(watched_span.span)
                self._drop_span_nolock(watchlist, index)
                continue

            # In terms of concurrency we are only really interested in the
            # span's end time, so we take a snapshot here and us it throughout
            # the span processor and exporter
            watched_span.update_end_time()

            # Many spans will be really short-lived and reporting start and end
            # in two separate export runs won't bring much benefit. Thus, defer
            # reporting new spans for at least one export cycle.
            if not watched_span.has_ended and not watched_span.is_older_than(
                one_interval_ago_nanos
            ):
                index += 1
                continue

            if watched_span.has_ended:
                self._drop_span_nolock(watchlist, index)
            else:
                index += 1

            if self._should_report_span(watched_span):
                yield watched_span

    @staticmethod
    def _drop_span_nolock(watchlist: List[WatchedSpan], index: int):
        watchlist[index] = watchlist[-1]
        watchlist.pop()

    @staticmethod
    def _current_nanos() -> int:
        return _time_ns()

    def _export(
        self, watched_spans: List[WatchedSpan], export_kind: ExportKind
    ) -> None:
        """Exports the given list of spans. The exporter is responsible for splitting into batches."""
        current_time_nanos = self._current_nanos()
        # Typically, the keep alive interval is a multiple of the report interval
        # but especially for unit test scenarios we need to consider keep alive
        # interval being smaller.
        min_send_interval_nanos = (
            min(self._report_interval_millis, self._keep_alive_interval_millis)
            * 1000000
        )

        min_creation_time_nanos = current_time_nanos - self._max_span_age_nanos
        one_interval_ago_nanos = current_time_nanos - min_send_interval_nanos
        self._export_batch(
            self._collect_spans_for_export(
                watched_spans,
                one_interval_ago_nanos=one_interval_ago_nanos,
                min_creation_time_nanos=min_creation_time_nanos,
            ),
            export_kind,
        )

    def _export_remaining_spans(self):
        with self._condition:
            self._pump_fresh_spans()

        self._export(self._span_watchlist, ExportKind.SHUTDOWN_OR_FLUSH)

    def shutdown(self) -> None:
        """Shuts down this :class:`DtSpanProcessor` and its associated
        :class:`dt_trace.WatchedSpanExporter` and flushes all spans.

        Shutdown must not be called more than once. An attempt is made to block
        repeated calls, but in particular, shutdown is not thread safe.
        """
        if self._done:
            processor_logger.warning(
                "Already shut down, ignoring call to shutdown()."
            )
            return
        # signal the worker thread to finish and then wait for it
        self._done = True
        with self._condition:
            self._condition.notify_all()
        self._join_worker()
        self._exporter.shutdown()

    def force_flush(self, timeout_millis: int = None) -> bool:
        """Processes all spans that have not yet been processed.

        This method will block the calling thread until either the flush
        operation finished or the given timeout expired.

        This method is thread-safe and may be called from multiple threads.

        Args:
            timeout_millis: the timeout in milliseconds to wait for the flush
                operation to finish.
        Returns:
            True if the flush operation finished within the given timeout, False
            otherwise.
        """
        if self._done:
            processor_logger.warning(
                "Already shut down, ignoring call to force_flush()."
            )
            return True

        if timeout_millis is None:
            timeout_millis = self._shutdown_or_flush_timeout_millis

        with self._condition:
            flush_request = self._get_or_create_flush_request()
            # signal the worker thread to flush and the wait for it to finish
            self._condition.notify_all()

        return flush_request.wait(timeout_millis / 1e3)

    def _join_worker(self):
        timeout_sec = self._shutdown_or_flush_timeout_millis / 1e3
        self._worker_thread.join(timeout=timeout_sec)


class _SpanKey:
    __slots__ = ("_trace_id", "_span_id")

    def __init__(self, span: ReadableSpan):
        span_context = span.get_span_context()
        self._trace_id = span_context.trace_id
        self._span_id = span_context.span_id

    def __eq__(self, other):
        return (
            self._trace_id == other._trace_id
            and self._span_id == other._span_id
        )

    def __hash__(self):
        return hash((self._trace_id, self._span_id))


class _WatchedSpanLookup:
    def __init__(self):
        self._lock = threading.Lock()
        self._lookup_dict = {}  # type: Dict[_SpanKey, WatchedSpan]

    def add(self, watched_span: WatchedSpan):
        key = _SpanKey(watched_span.span)
        with self._lock:
            self._lookup_dict[key] = watched_span
        return watched_span

    def remove(self, span: ReadableSpan) -> Optional[WatchedSpan]:
        key = _SpanKey(span)
        with self._lock:
            return self._lookup_dict.pop(key, None)

    def get(self, span: ReadableSpan) -> Optional[WatchedSpan]:
        key = _SpanKey(span)
        with self._lock:
            return self._lookup_dict.get(key)
