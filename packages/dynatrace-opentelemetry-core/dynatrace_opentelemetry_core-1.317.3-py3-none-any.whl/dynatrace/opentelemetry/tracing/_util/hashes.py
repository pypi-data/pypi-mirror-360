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

import hashlib

from dynatrace.opentelemetry.tracing._util.byteops import (
    as_bytes_us_ascii,
    uint32_to_int32,
)

_BIT_MASK_64 = (2 << 63) - 1
_MURMUR_MULT_CONST = 0xC6A4A7935BD1E995
_MURMUR_ROT_CONST = 47


def murmur2_64a(
    data: bytes,
    seed: int = 0xE17A1465,
    start_idx: int = None,
    end_idx: int = None,
) -> int:
    """Implementation of 64 bit murmur2 hash

    This implementation is compliant with the reference implementation given on
    https://github.com/aappleby/smhasher/blob/master/src/MurmurHash2.cpp
    """
    # pylint:disable=too-many-locals
    if start_idx is None:
        start_idx = 0
    if end_idx is None:
        end_idx = len(data)

    length = end_idx - start_idx

    hash_value = seed ^ ((length * _MURMUR_MULT_CONST) & _BIT_MASK_64)
    full_chunk_end_idx = start_idx + (length & 0xFFFFFFF8)

    idx = start_idx
    while idx < full_chunk_end_idx:
        bb0 = (data[idx] & 0xFF) | ((data[idx + 4] & 0xFF) << 32)
        bb1 = (data[idx + 1] & 0xFF) | ((data[idx + 5] & 0xFF) << 32)
        bb2 = (data[idx + 2] & 0xFF) | ((data[idx + 6] & 0xFF) << 32)
        bb3 = (data[idx + 3] & 0xFF) | ((data[idx + 7] & 0xFF) << 32)

        bbb0 = bb0 | (bb2 << 16)
        bbb1 = bb1 | (bb3 << 16)

        kb = bbb0 | (bbb1 << 8)

        kb = (kb * _MURMUR_MULT_CONST) & _BIT_MASK_64
        kb ^= (kb >> _MURMUR_ROT_CONST) & _BIT_MASK_64
        kb = (kb * _MURMUR_MULT_CONST) & _BIT_MASK_64

        hash_value ^= kb
        hash_value = (hash_value * _MURMUR_MULT_CONST) & _BIT_MASK_64

        idx += 8

    lr = length & 0x7
    if lr == 7:
        hash_value ^= (data[idx + 6] & 0xFF) << 48
    if lr >= 6:
        hash_value ^= (data[idx + 5] & 0xFF) << 40
    if lr >= 5:
        hash_value ^= (data[idx + 4] & 0xFF) << 32
    if lr >= 4:
        hash_value ^= (data[idx + 3] & 0xFF) << 24
    if lr >= 3:
        hash_value ^= (data[idx + 2] & 0xFF) << 16
    if lr >= 2:
        hash_value ^= (data[idx + 1] & 0xFF) << 8
    if lr >= 1:
        hash_value ^= data[idx] & 0xFF
        hash_value = (hash_value * _MURMUR_MULT_CONST) & _BIT_MASK_64

    hash_value ^= (hash_value >> _MURMUR_ROT_CONST) & _BIT_MASK_64
    hash_value = (hash_value * _MURMUR_MULT_CONST) & _BIT_MASK_64
    hash_value ^= (hash_value >> _MURMUR_ROT_CONST) & _BIT_MASK_64

    return hash_value


def tenant_id_hash(tenant_uuid: str) -> int:
    md5 = hashlib.md5()
    md5.update(as_bytes_us_ascii(tenant_uuid))

    digest = md5.digest()

    hash_value = 0
    for idx in range(0, 16):
        bit_shift = (3 - (idx & 3)) << 3  # 24, 16, 8, 0 respectively
        hash_value ^= (digest[idx] << bit_shift) & (0xFF << bit_shift)

    return uint32_to_int32(hash_value)
