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

import logging
import random
import time
import typing

from dynatrace.opentelemetry.tracing import version
from dynatrace.opentelemetry.tracing._config.reader import get_configuration
from dynatrace.opentelemetry.tracing._export.serialization import (
    serialize_for_export,
)
from dynatrace.opentelemetry.tracing._export.types import (
    ExportKind,
    SpanStream,
    WatchedSpanExporter,
)
from dynatrace.opentelemetry.tracing._logging.loggers import exporter_logger
from dynatrace.opentelemetry.tracing._otel.sdk import SpanExportResult
from dynatrace.opentelemetry.tracing._transport import exceptions
from dynatrace.opentelemetry.tracing._transport.pooling import PooledConnection
from dynatrace.opentelemetry.tracing._transport.response import HttpResponse
from dynatrace.opentelemetry.tracing._transport.timeout import Timeout

MSG_SIZE_MAX = 64 * 1024 * 1024  # 64 MB
MSG_SIZE_WARN = 1 * 1024 * 1024  # 1 MB

# for connection resets retry only if the send operation failed within this time
# limit. Otherwise we assume the backend is overloaded and do not retry.
_CONNECTION_RESET_TIME_LIMIT_MILLIS = 300


class DtSpanExporter(WatchedSpanExporter):
    """Implements an exporter for exporting spans to the Dynatrace backend."""

    def __init__(self, **kwargs):
        """Creates a new DtSpanExporter instance"""
        config = get_configuration(**kwargs)
        if not config.connection.span_endpoint_url:
            raise ValueError("Connection.BaseUrl not configured")
        if not config.qualified_tenant_id:
            raise ValueError("Tenant not configured")
        if not config.connection.auth_token:
            raise ValueError("Connection.AuthToken not configured")

        self._qualified_tenant_id = config.qualified_tenant_id
        self._span_endpoint_url = config.connection.span_endpoint_url
        self._is_export_disabled = False
        self._exporter_id = config.connection.exporter_id
        self._env_resources = config.env_resources
        token = config.connection.auth_token
        token_scheme = "Dynatrace "
        self._http_headers = {
            "Content-Type": "application/x-dt-span-export",
            "Authorization": token_scheme + token,
            "User-Agent": (
                f"odin-python/{version.FULL_VERSION} "
                f"0x{config.connection.exporter_id_unsigned:016x} "
                f"{self._qualified_tenant_id.tenant_uuid}"
            ),
            "Accept": "*/*; q=0",
        }
        self._verify_tls = config.connection.verify_tls
        self._connection = PooledConnection(
            config.connection.base_url,
            maxsize=1,  # max number of connections kept in one pool
            block=True,  # block if more than 1 (maxsize) connection
            retries=0,
            cert_reqs="CERT_REQUIRED" if self._verify_tls else "CERT_NONE",
        )
        self._retry_timeouts_millis = config.extra.retry_timeouts_millis
        self._regular_send_timeouts_sec = self.timeouts_millis_to_sec(
            config.extra.regular_send_timeouts_millis
        )
        self._flush_send_timeouts_sec = self.timeouts_millis_to_sec(
            (
                config.connection.flush_connect_timeout_millis,
                config.connection.flush_data_timeout_millis,
            )
        )

    @staticmethod
    def timeouts_millis_to_sec(
        timeouts_millis: typing.Tuple[int, int],
    ) -> Timeout:
        return Timeout(
            connect=timeouts_millis[0] / 1000, read=timeouts_millis[1] / 1000
        )

    def export(
        self, spans: SpanStream, export_kind: ExportKind
    ) -> SpanExportResult:
        """Sends the given sequence of spans to the predefined endpoint URL.

        This method will take the given spans and convert them to a
        corresponding protobuf representation. The protobuf object will then be
        transmitted via a HTTP post request.

        Args:
            spans: A sequence of tuples of :class:`dt_trace.WatchedSpan` and
                :class:`sdk_trace.Span` which are to be send to the configured
                endpoint.
            export_kind: The kind of export determining connection timeouts and
                retry handling.

        Raises:
            :class:`dynatrace.otel.http.exceptions.HttpError` if an HTTP error
                occurred when transmitting the data.
        """
        if self._is_export_disabled:
            exporter_logger.debug("Export disabled.")
            return SpanExportResult.FAILURE

        exporter_logger.debug("Starting to export spans.")
        export_start_sec = time.time()
        for export_data in serialize_for_export(
            spans,
            self._qualified_tenant_id,
            self._exporter_id,
            self._env_resources,
            MSG_SIZE_WARN,
            MSG_SIZE_MAX,
        ):
            serialized_data = export_data.SerializeToString()
            self._log_serialization_finished(serialized_data, export_start_sec)

            response_code = self._send_data(serialized_data, export_kind)
            if response_code < 200 or response_code > 299:
                return SpanExportResult.FAILURE

            self._log_export_success(response_code, export_start_sec)
            export_start_sec = time.time()
        return SpanExportResult.SUCCESS

    @staticmethod
    def _log_serialization_finished(
        serialized_data: bytes, serialization_start_sec: float
    ):
        exporter_logger.log(
            (
                logging.WARNING
                if len(serialized_data) > MSG_SIZE_WARN
                else logging.DEBUG
            ),
            "Serialized spans in %.6f sec to %s bytes",
            time.time() - serialization_start_sec,
            len(serialized_data),
        )

    @staticmethod
    def _log_export_success(response_code: int, export_start_sec: float):
        exporter_logger.debug(
            "Exported spans in %.06f sec, got HTTP response code %s",
            time.time() - export_start_sec,
            response_code,
        )

    def _send_data(
        self, serialized_data: bytes, export_kind: ExportKind
    ) -> int:
        """Tries to send the given serialized data to the configured endpoint.

        In case of certain errors while sending data a configured number of
        retries will be attempted (if retrying is allowed for the current export
        operation) with certain back-off times in between.

        Args:
            serialized_data: The serialized data encapsulating the spans to send.
            export_kind: The kind of export determining connection timeouts and
                retry handling.
        """
        current_retry = 0
        send_timeouts_sec = self.get_send_timeouts_sec(export_kind)
        while True:
            response_code = -1
            send_start_sec = time.time()
            try:
                response = self._connection.post(
                    self._span_endpoint_url,
                    headers=self._http_headers,
                    body=serialized_data,
                    timeout=send_timeouts_sec,
                )
                response_code = response.status
                if response_code < 200 or response_code > 299:
                    raise exceptions.HttpError(
                        f"POST: Unexpected response code HTTP {response_code} {response.reason}"
                    )

                self._log_send_finished(
                    response, send_start_sec, send_timeouts_sec
                )
                return response.status
            except exceptions.HttpError as exception:
                if response_code in (401, 403):
                    # situation will only improve if the token changes, so avoid
                    # further exporting
                    self._is_export_disabled = True
                    exporter_logger.error(
                        "Got HTTP %s, disabling export.", response_code
                    )
                    raise  # rethrow

                if (
                    isinstance(exception, exceptions.RemoteDisconnected)
                    and current_retry < 1
                    and self._elapsed_time_in_millis(send_start_sec)
                    <= _CONNECTION_RESET_TIME_LIMIT_MILLIS
                ):
                    exporter_logger.debug(
                        "Retrying export due to connection reset: %s",
                        exception,
                    )
                    current_retry += 1
                    continue

                if self.should_retry_export(
                    export_kind, current_retry, exception
                ):
                    timeout_sec = self._calc_retry_timeout_sec(current_retry)
                    self._log_retry_export(
                        timeout_sec, current_retry, exception
                    )
                    self._wait_retry_timeout_sec(timeout_sec)

                    current_retry += 1
                    continue
                self._log_failed_export(current_retry, exception)
                return response_code

    @staticmethod
    def _elapsed_time_in_millis(start_time_sec: float):
        return (time.time() - start_time_sec) * 1000

    def _log_send_finished(
        self,
        response: HttpResponse,
        send_start_sec: float,
        send_timeouts_sec: Timeout,
    ):
        send_duration_sec = time.time() - send_start_sec
        total_send_timeout_sec = (
            send_timeouts_sec.connect_timeout + send_timeouts_sec.read_timeout
        )
        if send_duration_sec > (total_send_timeout_sec / 3):
            log_func = exporter_logger.warning
        else:
            log_func = exporter_logger.debug
        log_func(
            "Got HTTP response code %s after %.06f sec"
            " (timeouts: connect=%s sec, read=%s sec)",
            response.status,
            send_duration_sec,
            send_timeouts_sec.connect_timeout,
            send_timeouts_sec.read_timeout,
        )
        self._log_if_unexpected_response(response)

    @staticmethod
    def _log_retry_export(
        timeout_sec: float, current_retry: int, exception: Exception
    ):
        exporter_logger.debug(
            "Retryable failure in export."
            " Sleeping for %s sec before retry#%s...",
            timeout_sec,
            current_retry + 1,
            exc_info=exception,
        )

    @staticmethod
    def _log_failed_export(current_retry: int, exception: Exception):
        exporter_logger.warning(
            "Failed to export spans after %s retries",
            current_retry,
            exc_info=exception,
        )

    @staticmethod
    def _log_if_unexpected_response(response: HttpResponse):
        if not exporter_logger.isEnabledFor(logging.WARNING):
            return
        content_type = response.headers.get("content-type")
        content_length_str = response.headers.get("content-length", "-1")
        try:
            content_length = int(content_length_str)
        except (ValueError, TypeError) as ex:
            exporter_logger.warning(
                "Content-Length %s is not numeric: %s",
                content_length_str,
                str(ex),
            )
            content_length = -1

        if content_length <= 0 and not content_type:
            return

        exporter_logger.warning(
            "Unexpectedly got HTTP response with Content-Length: %s, "
            "Content-Type: %s",
            content_length,
            content_type,
        )

    def get_send_timeouts_sec(self, export_kind: ExportKind) -> Timeout:
        if export_kind == ExportKind.REGULAR:
            return self._regular_send_timeouts_sec
        if export_kind == ExportKind.SHUTDOWN_OR_FLUSH:
            return self._flush_send_timeouts_sec
        raise ValueError("Unhandled ExportKind " + export_kind.name)

    def should_retry_export(
        self,
        export_kind: ExportKind,
        current_retry: int,
        exception: exceptions.HttpError,
    ) -> bool:
        """Checks if the export should be retried.

        Args:
            export_kind: The kind of export determining whether retrying is
                principally possible or not.
            current_retry: The number of retries so far.
            exception: The exception which happened during sending the data and
                which is the cause for checking if a retry should be done.
        Returns: True if a retry should be done, False otherwise.
        """
        if export_kind != ExportKind.REGULAR or current_retry >= len(
            self._retry_timeouts_millis
        ):
            return False

        if not isinstance(exception, exceptions.ProtocolError):
            return False

        return not isinstance(exception, exceptions.TimeoutError)

    @staticmethod
    def _wait_retry_timeout_sec(timeout_sec: float):
        time.sleep(timeout_sec)

    def _calc_retry_timeout_sec(self, current_retry: int) -> float:
        """Calculates the retry back-off timeout in seconds for the current
        retry.
        """
        retry_timeout_millis, jitter_millis = self._retry_timeouts_millis[
            current_retry
        ]
        rnd_jitter_millis = random.randint(-jitter_millis, jitter_millis)
        return (retry_timeout_millis + rnd_jitter_millis) / 1000

    def shutdown(self):
        self._connection.close()
