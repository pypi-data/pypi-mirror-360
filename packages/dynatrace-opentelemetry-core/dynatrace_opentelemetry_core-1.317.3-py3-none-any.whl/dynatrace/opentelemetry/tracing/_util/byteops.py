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

import binascii

_BYTE_ORDER_BIG_ENDIAN = "big"

MASK_16BIT = 2**16 - 1
MASK_32BIT = 2**32 - 1
MASK_64BIT = 2**64 - 1
MASK_128BIT = 2**128 - 1

SIGNED_INT32_MAX = 0x7FFFFFFF
SIGNED_INT32_MIN = -0x80000000
INT32_UNSIGNED_TO_SIGNED_CONST = 0x100000000

_ENCODING_US_ASCII = "us-ascii"


def to_16bit_padded_hex_str(value: int) -> str:
    return format(value & MASK_16BIT, "04x")


def to_32bit_hex_str(value: int) -> str:
    return format(value & MASK_32BIT, "x")


def to_64bit_be(value: int) -> bytes:
    return (value & MASK_64BIT).to_bytes(8, _BYTE_ORDER_BIG_ENDIAN)


def to_64bit_be_hex_str(value: int) -> str:
    value_as_be_bytes = to_64bit_be(value)
    return bytes_to_hex_str(value_as_be_bytes)


def to_128bit_be(value: int) -> bytes:
    return (value & MASK_128BIT).to_bytes(16, _BYTE_ORDER_BIG_ENDIAN)


def to_128bit_be_hex_str(value: int) -> str:
    value_as_be_bytes = to_128bit_be(value)
    return bytes_to_hex_str(value_as_be_bytes)


def bytes_to_hex_str(value: bytes) -> str:
    hexlified = binascii.hexlify(value)
    return hexlified.decode(_ENCODING_US_ASCII)


def as_bytes_us_ascii(value: str) -> bytes:
    return value.encode(_ENCODING_US_ASCII, "replace")


def _from32_bit_hex_str(value: str, aligned: bool) -> int:
    value_len = len(value)
    if aligned and value_len % 2 != 0:
        raise ValueError("Invalid hex int value: odd length.")
    if value_len > 8:
        raise ValueError("Invalid hex int value: overflow.")
    if value.startswith("-"):
        raise ValueError("invalid character")

    int_value = uint32_to_int32(int(value, 16))
    return int_value


def from_32bit_hex_str_aligned(value: str) -> int:
    return _from32_bit_hex_str(value, aligned=True)


def from_32_bit_hex_str(value: str) -> int:
    return _from32_bit_hex_str(value, aligned=False)


def from_64_bit_hex_str(value: str) -> int:
    if len(value) > 16:  # 1 char == 4 bit
        raise ValueError("Invalid hex int value: overflow.")

    return int(value, 16)


def from_128_bit_hex_str(value: str) -> int:
    if len(value) > 32:  # 1 char == 4 bit
        raise ValueError("Invalid hex int value: overflow.")

    return int(value, 16)


def bytes_from_hex_str(value: str) -> bytes:
    if len(value) % 2 != 0:
        raise ValueError("Invalid hex value: odd length.")
    return bytes.fromhex(value)


def from_32bit_int_str(value: str) -> int:
    int_value = int(value)
    if int_value > SIGNED_INT32_MAX or int_value < SIGNED_INT32_MIN:
        raise ValueError("Int32 value out of range")
    return int_value


def to_32bit_int_str(int_value: int) -> str:
    if int_value > SIGNED_INT32_MAX or int_value < SIGNED_INT32_MIN:
        raise ValueError("Int32 value out of range")
    return str(int_value)


def uint32_to_int32(int_value: int) -> int:
    if int_value > SIGNED_INT32_MAX:
        int_value -= INT32_UNSIGNED_TO_SIGNED_CONST
    return int_value


def int32_to_uint32(int_value: int) -> int:
    return int_value & MASK_32BIT
