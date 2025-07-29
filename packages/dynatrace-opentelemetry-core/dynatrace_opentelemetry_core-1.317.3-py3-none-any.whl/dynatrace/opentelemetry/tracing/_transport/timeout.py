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

import typing


class Timeout:
    def __init__(self, connect: float = None, read: float = None):
        self.connect_timeout = connect
        self.read_timeout = read

    @property
    def total(self) -> typing.Optional[float]:
        if self.connect_timeout is None and self.read_timeout is None:
            return None
        timeout = 0
        if self.connect_timeout is not None:
            timeout += self.connect_timeout
        if self.read_timeout is not None:
            timeout += self.read_timeout
        return timeout


DEFAULT_TIMEOUT = Timeout()
