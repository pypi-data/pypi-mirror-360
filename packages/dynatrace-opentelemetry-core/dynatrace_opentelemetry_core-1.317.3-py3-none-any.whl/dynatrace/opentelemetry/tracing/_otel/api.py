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

import importlib
import warnings

_OTEL_BASE_NAMESPACE = "dynatraceotel"
try:
    importlib.import_module(_OTEL_BASE_NAMESPACE)
except ImportError:
    _OTEL_BASE_NAMESPACE = "opentelemetry"

    from opentelemetry import context as _context
    from opentelemetry import propagate as _propagate
    from opentelemetry import trace as _trace
    from opentelemetry.propagators import textmap as _textmap
    from opentelemetry.trace import propagation as _propagation
    from opentelemetry.trace import span as _span
    from opentelemetry.trace import status as _status
    from opentelemetry.trace.propagation import tracecontext as _tracecontext
    from opentelemetry.util import types as _types
else:
    from dynatraceotel import context as _context
    from dynatraceotel import propagate as _propagate
    from dynatraceotel import trace as _trace
    from dynatraceotel.propagators import textmap as _textmap
    from dynatraceotel.trace import propagation as _propagation
    from dynatraceotel.trace import span as _span
    from dynatraceotel.trace import status as _status
    from dynatraceotel.trace.propagation import tracecontext as _tracecontext
    from dynatraceotel.util import types as _types


# trace
Link = _trace.Link
SpanKind = _trace.SpanKind
Tracer = _trace.Tracer
set_tracer_provider = _trace.set_tracer_provider

# trace.propagate
get_global_textmap = _propagate.get_global_textmap
set_global_textmap = _propagate.set_global_textmap

# trace.propagation
get_current_span = _propagation.get_current_span
set_span_in_context = _propagation.set_span_in_context

# trace.propagation.tracecontext
TraceContextTextMapPropagator = _tracecontext.TraceContextTextMapPropagator

# trace.span
NonRecordingSpan = _span.NonRecordingSpan
Span = _span.Span
SpanContext = _span.SpanContext

TraceFlags = _span.TraceFlags
TraceState = _span.TraceState

DEFAULT_TRACE_STATE = _span.DEFAULT_TRACE_STATE
INVALID_SPAN = _span.INVALID_SPAN
INVALID_TRACE_ID = _span.INVALID_TRACE_ID
INVALID_SPAN_ID = _span.INVALID_SPAN_ID
INVALID_SPAN_CONTEXT = _span.INVALID_SPAN_CONTEXT

format_trace_id = _span.format_trace_id
format_span_id = _span.format_span_id

# context
Context = _context.Context
attach = _context.attach
detach = _context.detach
get_value = _context.get_value
set_value = _context.set_value

# ### create_key is only available in 1.4+ ###
create_key = getattr(_context, "create_key", lambda key: key)

# trace.status
StatusCode = _status.StatusCode

# propagators.textmap
CarrierT = _textmap.CarrierT
Getter = _textmap.Getter
Setter = _textmap.Setter

TextMapPropagator = _textmap.TextMapPropagator

default_getter = _textmap.default_getter
default_setter = _textmap.default_setter

# util
Attributes = _types.Attributes
AttributeValue = _types.AttributeValue


# suppress instrumentation key
def _get_suppress_instrumentation_key() -> str:
    attr_key = "_SUPPRESS_INSTRUMENTATION_KEY"

    key = getattr(_context, attr_key, None)  # from 1.7+ it is in here
    if key is not None:
        return key

    try:
        # versions 1.4 to 1.6 had it in instrumentation package
        instr_module = importlib.import_module(
            f"{_OTEL_BASE_NAMESPACE}.instrumentation.utils"
        )
        key = getattr(instr_module, attr_key, None)
    except ImportError:
        pass

    if key is not None:
        return key

    # this is either OTel version < 1.4 or the field was moved/renamed
    warnings.warn(
        "'_SUPPRESS_INSTRUMENTATION_KEY' not in OTel API, "
        "span suppression might not work"
    )
    return create_key("suppress_instrumentation")


_SUPPRESS_INSTRUMENTATION_KEY = _get_suppress_instrumentation_key()
