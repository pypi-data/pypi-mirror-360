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

import contextlib
import io
from types import FrameType
from typing import Dict, Optional, Tuple

import dynatrace.odin.semconv.v1 as semconv
from dynatrace.opentelemetry.tracing._logging.loggers import core_logger
from dynatrace.opentelemetry.tracing._otel.api import Span

_MAX_EXCEPTION_DEPTH = 11
_MAX_STACKTRACE_SIZE = 60 * 1024


@contextlib.contextmanager
def record_on(span: Span):
    try:
        yield
    except Exception as ex:  # pylint: disable=broad-except
        record_exception(span, ex)
        raise


def record_exception(span: Span, exception: BaseException):
    if (
        not span
        or not span.is_recording()
        or not isinstance(exception, BaseException)
    ):
        return
    try:
        _record_exception(span, exception)
    except Exception as ex:  # pylint:disable=broad-except
        core_logger.warning("Failed to record exception", exc_info=ex)


def _record_exception(span: Span, exception: BaseException):
    span.set_attribute(
        semconv.DT_EXCEPTION_SERIALIZED_STACKTRACES,
        _serialize_stack_traces(exception),
    )
    types = io.StringIO()
    messages = io.StringIO()

    for current_exc, is_first in _iterate_exceptions(exception):
        if not is_first:
            types.write("\n")
            messages.write("\n")

        _append_exception_info(current_exc, messages, types)

    span.set_attribute(semconv.DT_EXCEPTION_TYPES, types.getvalue())
    span.set_attribute(semconv.DT_EXCEPTION_MESSAGES, messages.getvalue())


def _append_exception_info(
    exception: BaseException, messages: io.StringIO, types: io.StringIO
):
    exc_type = type(exception)
    exc_module = exc_type.__module__ or "<unknown_module>"
    qualified_exc_type = exc_module + "." + type(exception).__qualname__
    types.write(escape_delimiters(qualified_exc_type, escape_tabs=False))

    message = _get_message(exception)
    if message is None:
        messages.write("0")
    else:
        line_count = message.count("\n") + 1
        messages.write(str(line_count))
        messages.write("\n")
        messages.write(message)


def _get_message(exception: BaseException) -> Optional[str]:
    try:
        return str(exception)
    except Exception:  # pylint:disable=broad-except
        return None


def _serialize_stack_traces(exception: BaseException) -> str:
    serialized_stacktraces = io.StringIO()
    seen_lines: Dict[Tuple[int, int], int] = {}
    line_index = 0
    max_size_reached = False

    for current_exc, _ in _iterate_exceptions(exception):
        for frame, line_number in _iterate_stacktrace(current_exc):
            line_key = _make_stack_trace_line_key(frame, line_number)
            ref_line_index = seen_lines.get(line_key, None)
            if ref_line_index is None:
                _write_stack_trace_line(
                    frame, line_number, serialized_stacktraces
                )
                seen_lines[line_key] = line_index
                line_index += 1
            else:
                serialized_stacktraces.write(str(ref_line_index))
            serialized_stacktraces.write("\n")

            if serialized_stacktraces.tell() > _MAX_STACKTRACE_SIZE:
                max_size_reached = True
                break

        if max_size_reached:
            break
        serialized_stacktraces.write("\n")

    return serialized_stacktraces.getvalue()


def _iterate_exceptions(exception: BaseException):
    current_exc = exception
    exc_depth = 0
    while current_exc is not None and exc_depth < _MAX_EXCEPTION_DEPTH:
        yield current_exc, exc_depth == 0
        exc_depth += 1
        current_exc = _get_next_exception_from(current_exc)


def _get_next_exception_from(
    exception: BaseException,
) -> Optional[BaseException]:
    return exception.__cause__ or exception.__context__


def _iterate_stacktrace(exception: BaseException):
    current_tb = exception.__traceback__
    current_frame = None if current_tb is None else current_tb.tb_frame
    reversed_tracebacks = []

    while current_tb is not None:
        reversed_tracebacks.append(current_tb)
        current_tb = current_tb.tb_next
    reversed_tracebacks.reverse()

    # start from the most recent call
    for traceback in reversed_tracebacks:
        yield traceback.tb_frame, traceback.tb_lineno

    while current_frame is not None:
        yield current_frame, current_frame.f_lineno
        current_frame = current_frame.f_back


def _make_stack_trace_line_key(frame: FrameType, line_number: int):
    return id(frame.f_code), line_number


def _write_stack_trace_line(
    frame: FrameType, line_number: int, writer: io.StringIO
):
    code = frame.f_code

    method_name = escape_delimiters(code.co_name)
    class_name = ""  # not reliably/efficiently possible to detect the class
    writer.write(class_name)
    writer.write("\t")
    writer.write(method_name)

    filename = code.co_filename
    if filename is None:
        return
    writer.write("\t")
    filename = escape_delimiters(code.co_filename) or "<unknown>"
    writer.write(filename)

    if line_number is not None and line_number >= 0:
        writer.write("\t")
        writer.write(str(line_number))


def escape_delimiters(name: str, escape_tabs=True) -> str:
    if not name:
        return ""
    name = name.replace("%", "%25").replace("\n", "%0a")
    if escape_tabs:
        name = name.replace("\t", "%09")
    return name
