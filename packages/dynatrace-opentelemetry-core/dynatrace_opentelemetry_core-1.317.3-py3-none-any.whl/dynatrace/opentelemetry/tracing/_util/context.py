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
from types import MappingProxyType
from typing import Dict, Iterator, Mapping, Optional

from dynatrace.opentelemetry.tracing._otel.api import (
    _SUPPRESS_INSTRUMENTATION_KEY,
    AttributeValue,
    Context,
    attach,
    create_key,
    detach,
    get_value,
    set_value,
)
from dynatrace.opentelemetry.tracing._propagator.tags import RumTag

_EMPTY_DICT = MappingProxyType({})

TRACING_SUPPRESSION_KEY = create_key("dt-suppress-tracing")
_CTX_PROPAGATED_RES_ATTRS_KEY = create_key("dt-propagated-resource-attributes")
_CTX_RUM_TAG_KEY = create_key("dynatrace-rum-tag")


def get_ctx_rum_tag(context: Context) -> Optional["RumTag"]:
    return get_value(_CTX_RUM_TAG_KEY, context)


def set_ctx_rum_tag(context: Context, rum_tag: RumTag) -> Context:
    return set_value(_CTX_RUM_TAG_KEY, rum_tag, context)


def get_propagated_resource_attributes(
    context: Optional[Context] = None,
) -> Mapping:
    return get_value(_CTX_PROPAGATED_RES_ATTRS_KEY, context) or _EMPTY_DICT


def set_propagated_resource_attributes(
    attrs: Dict[str, AttributeValue], context: Optional[Context] = None
) -> Context:
    """Sets the given attributes in the given context so that they can be
    propagated to all locally started (child) spans. Make sure that the given
    context is properly activated.The attributes are added to the span only at
    export time.
    """
    if not attrs:
        return context

    return set_value(
        _CTX_PROPAGATED_RES_ATTRS_KEY, MappingProxyType(attrs.copy()), context
    )


@contextlib.contextmanager
def propagate_resource_attributes(
    attrs: Dict[str, AttributeValue], context: Context = None
) -> Iterator[Context]:
    """Sets the given attributes in the active context from where they will
    get propagated in the DtSpanProcessor to all locally started (child) span.
    The attributes are added to the span only at export time.
    """
    propagating_context = set_propagated_resource_attributes(attrs, context)
    token = attach(propagating_context)
    try:
        yield propagating_context
    finally:
        detach(token)


@contextlib.contextmanager
def suppressed_tracing():
    """Suppress recording of spans by updating the current `Context`.

    Sets a context variable to indicate tracers that only suppressed spans should
    be created. A suppressed span is a noop span with the same span context as
    the current active span.

    Sets a context variable to indicate that sensors should skip instrumentation
    code and call the instrumented library directly.
    """
    # instruct sensors to bypass instrumentation (not all sensors might comply)
    context = set_value(_SUPPRESS_INSTRUMENTATION_KEY, True)
    # instruct the tracer to only create suppressed spans
    context = set_value(TRACING_SUPPRESSION_KEY, True, context=context)
    token = attach(context)
    try:
        yield
    finally:
        detach(token)


def is_tracing_suppressed() -> bool:
    return bool(
        get_value(_SUPPRESS_INSTRUMENTATION_KEY)
        or get_value(TRACING_SUPPRESSION_KEY)
    )
