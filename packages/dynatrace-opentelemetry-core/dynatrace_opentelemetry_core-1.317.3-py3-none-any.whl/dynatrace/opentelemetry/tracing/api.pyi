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

from opentelemetry.context.context import Context
from opentelemetry.propagators.textmap import (
    CarrierT,
    Getter,
    Setter,
    TextMapPropagator,
    default_getter,
    default_setter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased

def configure_dynatrace(
    resource: Optional[Resource] = None,
) -> TracerProvider: ...

class DtTextMapPropagator(TextMapPropagator):
    def extract(
        self,
        carrier: CarrierT,
        context: Optional[Context] = None,
        getter: Getter = default_getter,
    ) -> Context: ...
    def inject(
        self,
        carrier: CarrierT,
        context: Optional[Context] = None,
        setter: Setter = default_setter,
    ): ...
    def fields(self) -> Set[str]: ...

class DtSampler(ParentBased):
    def __init__(self) -> DtSampler: ...

class DtSpanProcessor(SpanProcessor):
    def __init__(self) -> DtSpanProcessor: ...
