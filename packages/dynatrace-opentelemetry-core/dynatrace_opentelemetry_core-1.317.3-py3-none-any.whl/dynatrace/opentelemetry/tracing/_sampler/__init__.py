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

from typing import Optional, Sequence

from dynatrace.opentelemetry.tracing._otel.api import (
    Attributes,
    Context,
    Link,
    SpanKind,
    TraceState,
    get_current_span,
)
from dynatrace.opentelemetry.tracing._otel.sdk import (
    Decision,
    ParentBased,
    Sampler,
    SamplingResult,
)
from dynatrace.opentelemetry.tracing._util.meta import DtTraceState


class _DtStaticSampler(Sampler):
    def __init__(self, decision: Decision):
        self._decision = decision

    def should_sample(
        self,
        parent_context: Optional[Context],
        trace_id: int,
        name: str,
        kind: SpanKind = None,
        attributes: Attributes = None,
        links: Sequence[Link] = None,
        trace_state: TraceState = None,
    ) -> SamplingResult:
        return SamplingResult(
            self._decision, attributes, _get_trace_state(parent_context)
        )

    def get_description(self) -> str:
        if self._decision is Decision.DROP:
            return "DtAlwaysOffSampler"
        return "DtAlwaysOnSampler"


class _DtFw4TagSampler(Sampler):
    def should_sample(
        self,
        parent_context: Optional[Context],
        trace_id: int,
        name: str,
        kind: SpanKind = None,
        attributes: Attributes = None,
        links: Sequence[Link] = None,
        trace_state: TraceState = None,
    ) -> SamplingResult:
        trace_state = _get_trace_state(parent_context)
        decision = (
            Decision.DROP
            if _ignore_span(trace_state)
            else Decision.RECORD_AND_SAMPLE
        )
        return SamplingResult(decision, attributes, trace_state)

    def get_description(self) -> str:
        return "DtFw4TagSampler"


def _get_trace_state(parent_context: Optional[Context]) -> DtTraceState:
    parent_span = get_current_span(parent_context)
    trace_state = parent_span.get_span_context().trace_state
    if isinstance(trace_state, DtTraceState):
        return trace_state

    return DtTraceState(trace_state.items())


def _ignore_span(trace_state: Optional[DtTraceState]) -> bool:
    if trace_state is None or trace_state.dt_fw4_tag is None:
        return False
    return trace_state.dt_fw4_tag.is_ignored


_DT_ALWAYS_ON = _DtStaticSampler(Decision.RECORD_AND_SAMPLE)
_DT_ALWAYS_OFF = _DtStaticSampler(Decision.DROP)
_FW4_TAG_SAMPLER = _DtFw4TagSampler()


class DtSampler(ParentBased):
    def __init__(self):
        super().__init__(
            root=_DT_ALWAYS_ON,
            remote_parent_sampled=_FW4_TAG_SAMPLER,
            remote_parent_not_sampled=_FW4_TAG_SAMPLER,
            local_parent_sampled=_DT_ALWAYS_ON,
            local_parent_not_sampled=_DT_ALWAYS_OFF,
        )


DT_SAMPLER = DtSampler()
