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


class HttpError(Exception):
    pass


class SSLError(HttpError):
    pass


class ProtocolError(HttpError):
    pass


class RemoteDisconnected(ProtocolError):
    pass


class TimeoutError(HttpError):
    # pylint: disable=redefined-builtin
    pass


class ConnectTimeoutError(TimeoutError):
    pass


class ReadTimeoutError(TimeoutError):
    pass


class NewConnectionError(ConnectTimeoutError):
    pass


class LocationValueError(HttpError, ValueError):
    pass


class PoolError(HttpError):
    pass


class EmptyPoolError(PoolError):
    pass


class ClosedPoolError(PoolError):
    pass


class HostChangedError(PoolError):
    pass
