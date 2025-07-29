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

from dynatrace.opentelemetry.tracing._util.hashes import tenant_id_hash

_mask_64_bit = 2**64 - 1


class QualifiedTenantId:
    def __init__(self, cluster_id: int, tenant_uuid: str):
        self._cluster_id = cluster_id
        self._tenant_uuid = tenant_uuid
        self._tenant_id = tenant_id_hash(tenant_uuid)

    @property
    def cluster_id(self) -> int:
        """Returns the identifier of the cluster to which spans are reported."""
        return self._cluster_id

    @property
    def cluster_id_unsigned(self) -> int:
        return self._cluster_id & _mask_64_bit

    @property
    def tenant_uuid(self):
        """Returns the UUID of the tenant for which spans are reported."""
        return self._tenant_uuid

    @property
    def tenant_id(self) -> int:
        """Returns the ID of the tenant for which spans are reported.

        The tenant ID corresponds to the hashed tenant UUID.
        """
        return self._tenant_id

    @property
    def tenant_id_unsigned(self):
        return self._tenant_id & _mask_64_bit
