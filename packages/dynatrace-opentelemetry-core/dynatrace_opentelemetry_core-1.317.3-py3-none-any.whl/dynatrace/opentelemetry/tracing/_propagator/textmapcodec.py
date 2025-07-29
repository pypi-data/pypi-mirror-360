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

from dynatrace.opentelemetry.tracing._otel.api import TraceState
from dynatrace.opentelemetry.tracing._propagator.tags import (
    Fw4ExtFields,
    Fw4Tag,
    Fw4TagKind,
    get_trace_state_key,
)
from dynatrace.opentelemetry.tracing._util import byteops
from dynatrace.opentelemetry.tracing._util.hashes import murmur2_64a
from dynatrace.opentelemetry.tracing._util.tenant import QualifiedTenantId

################################################################################
# Decode
################################################################################


def _parse_tag_extension(tag: Fw4Tag, ext_id: int, hex_val: str):
    if ext_id == Fw4ExtFields.CUSTOM_BLOB.value:
        blob_len = len(hex_val)
        if blob_len > Fw4Tag.MAX_BLOB_LENGTH * 2:
            raise ValueError(f"Max blob size exceeded: {blob_len}")
        tag.custom_blob = byteops.bytes_from_hex_str(hex_val)

    elif ext_id == Fw4ExtFields.TAG_DEPTH.value:
        tag.tag_depth = byteops.from_32bit_hex_str_aligned(hex_val)

    elif ext_id == Fw4ExtFields.ENTRY_AGENT_ID.value:
        tag.entry_agent_id = byteops.from_32bit_hex_str_aligned(hex_val)

    elif ext_id == Fw4ExtFields.ENTRY_TAG_ID.value:
        tag.entry_tag_id = byteops.from_32bit_hex_str_aligned(hex_val)

    elif ext_id == Fw4ExtFields.PAYLOAD_BIT_SET.value:
        tag.payload_bit_set = byteops.from_32bit_hex_str_aligned(hex_val)

    elif ext_id == Fw4ExtFields.TRACE_ID.value:
        tag.trace_id = byteops.from_128_bit_hex_str(hex_val)

    elif ext_id == Fw4ExtFields.SPAN_ID.value:
        tag.span_id = byteops.from_64_bit_hex_str(hex_val)


def _parse_tag_extensions(tag: Fw4Tag, tokenizer: "StringTokenizer"):
    checksum_token = tokenizer.next_token
    if checksum_token is None:
        return

    if len(checksum_token) != 4:
        raise ValueError("Bad checksum: Invalid length")

    expected_checksum = int(checksum_token, 16)
    remaining_bytes = byteops.as_bytes_us_ascii(tokenizer.remainder(offset=-1))
    actual_checksum = murmur2_64a(remaining_bytes) & byteops.MASK_16BIT

    if actual_checksum != expected_checksum:
        raise ValueError(
            f"Checksum mismatch, expected {expected_checksum:0x} but was {actual_checksum:0x}"
        )

    while True:
        token = tokenizer.next_token
        if not token:
            break

        pos_h = token.find("h")
        if pos_h <= 0:
            continue

        extension_id = int(token[0:pos_h], 10)
        value = token[pos_h + 1 :]
        _parse_tag_extension(tag, extension_id, value)


def _parse_tag(tag_string: str) -> Fw4Tag:
    if not tag_string or not tag_string.startswith("fw4;"):
        raise ValueError("FW4 tag not found or has wrong format.")

    tokenizer = StringTokenizer(tag_string)
    tokenizer.skip_token()  # skip fw4 token

    tag = Fw4Tag()
    tag.server_id = tokenizer.next_int32_hex()
    tag.agent_id = tokenizer.next_int32_hex()
    tag.tag_id = tokenizer.next_int32_hex()
    tag.encoded_link_id = tokenizer.next_int32_hex()
    tag.encoded_link_id |= tokenizer.next_int32_hex() << 31
    tag.encoded_link_id |= tokenizer.next_int32_hex() << 27
    tag.encoded_link_id = byteops.uint32_to_int32(tag.encoded_link_id)
    tag.path_info = tokenizer.next_int32_hex()

    _parse_tag_extensions(tag, tokenizer)

    return tag


def parse_x_dynatrace(header: str):
    if not header or not header.startswith("FW4;"):
        raise ValueError("Header is none or has wrong format.")

    tokenizer = StringTokenizer(header)
    tokenizer.skip_token()  # skip FW4 token

    tag = Fw4Tag()
    tag.cluster_id = tokenizer.next_int32()
    tag.server_id = tokenizer.next_int32()
    tag.agent_id = tokenizer.next_int32()
    tag.tag_id = tokenizer.next_int32()
    tag.encoded_link_id = tokenizer.next_int32()
    tag.tenant_id = tokenizer.next_int32()
    tag.path_info = tokenizer.next_int32()

    _parse_tag_extensions(tag, tokenizer)

    return tag


def from_trace_state(
    trace_state: TraceState, qualified_tenant_id: QualifiedTenantId
) -> typing.Optional[Fw4Tag]:
    key = get_trace_state_key(qualified_tenant_id)
    tag_string = trace_state.get(key, None)
    if not tag_string:
        return None

    tag = _parse_tag(tag_string)
    tag.set_qualified_tenant_id(qualified_tenant_id)

    return tag


class StringTokenizer:
    def __init__(self, data: str, separator=";"):
        self.data = data
        self.separator = separator
        self.current_position = 0

    def _next_token(self, extract_token: bool) -> typing.Optional[str]:
        if self.current_position > len(self.data):
            return None

        separator_pos = self.data.find(self.separator, self.current_position)
        next_idx = separator_pos if separator_pos >= 0 else len(self.data)
        token = None
        if extract_token:
            token = self.data[self.current_position : next_idx]
        self.current_position = next_idx + 1
        return token

    def skip_token(self):
        self._next_token(extract_token=False)

    @property
    def next_token(self) -> typing.Optional[str]:
        return self._next_token(extract_token=True)

    def next_int32_hex(self) -> int:
        token = self.next_token
        if not token:
            raise ValueError("Unexpected end of string")
        return byteops.from_32_bit_hex_str(token)

    def next_int32(self):
        token = self.next_token
        if not token:
            raise ValueError("Unexpected end of string")
        return byteops.from_32bit_int_str(token)

    def remainder(self, offset=0) -> str:
        return self.data[self.current_position + offset :]


################################################################################
# Encode
################################################################################


def append_hex_blob(data: bytes, string_list: typing.List[str]) -> None:
    hex_str = byteops.bytes_to_hex_str(data)
    string_list.append(hex_str)


def append_int32_hex(value: int, string_list: typing.List[str]) -> None:
    hex_str = byteops.to_32bit_hex_str(value)
    if len(hex_str) % 2 != 0:
        string_list.append("0")
    string_list.append(hex_str)


def _append_tlv_header(
    field: Fw4ExtFields, string_list: typing.List[str]
) -> None:
    string_list.append(";")
    string_list.append(str(field.value))
    string_list.append("h")


def _append_custom_blob(tag: Fw4Tag, string_list: typing.List[str]):
    if not tag.custom_blob:
        return
    _append_tlv_header(Fw4ExtFields.CUSTOM_BLOB, string_list)
    append_hex_blob(tag.custom_blob, string_list)


def _append_tag_depth(tag: Fw4Tag, string_list: typing.List[str]):
    if not tag.has_tag_depth:
        return
    _append_tlv_header(Fw4ExtFields.TAG_DEPTH, string_list)
    append_int32_hex(tag.tag_depth, string_list)


def _append_entry_agent_id(tag: Fw4Tag, string_list: typing.List[str]):
    if not tag.has_entry_agent_id:
        return
    _append_tlv_header(Fw4ExtFields.ENTRY_AGENT_ID, string_list)
    append_int32_hex(tag.entry_agent_id, string_list)


def _append_entry_tag_id(tag: Fw4Tag, string_list: typing.List[str]):
    if not tag.has_entry_tag_id:
        return
    _append_tlv_header(Fw4ExtFields.ENTRY_TAG_ID, string_list)
    append_int32_hex(tag.entry_tag_id, string_list)


def _append_payload_bitset(tag: Fw4Tag, string_list: typing.List[str]):
    if not tag.has_payload_bit_set:
        return
    _append_tlv_header(Fw4ExtFields.PAYLOAD_BIT_SET, string_list)
    append_int32_hex(tag.payload_bit_set, string_list)


def _append_trace_id(tag: Fw4Tag, string_list: typing.List[str]):
    if not tag.has_trace_id:
        return
    _append_tlv_header(Fw4ExtFields.TRACE_ID, string_list)
    string_list.append(byteops.to_128bit_be_hex_str(tag.trace_id))


def _append_span_id(tag: Fw4Tag, string_list: typing.List[str]):
    if not tag.has_span_id:
        return
    _append_tlv_header(Fw4ExtFields.SPAN_ID, string_list)
    string_list.append(byteops.to_64bit_be_hex_str(tag.span_id))


def _encode_extensions(
    tag: Fw4Tag, string_list: typing.List[str], tag_kind: Fw4TagKind
):
    if not tag.has_any_extension(tag_kind):
        return

    tag_list = []
    _append_custom_blob(tag, tag_list)
    _append_tag_depth(tag, tag_list)
    _append_entry_agent_id(tag, tag_list)
    _append_entry_tag_id(tag, tag_list)
    _append_payload_bitset(tag, tag_list)
    if tag_kind != Fw4TagKind.TRACE_STATE:
        # trace_id is redundant for tracestate, so don't serialize it
        _append_trace_id(tag, tag_list)
    _append_span_id(tag, tag_list)

    tag_string = "".join(tag_list)
    checksum = (
        murmur2_64a(byteops.as_bytes_us_ascii(tag_string)) & byteops.MASK_16BIT
    )

    string_list.append(";")
    string_list.append(byteops.to_16bit_padded_hex_str(checksum))
    string_list.append(tag_string)


def to_trace_state_value(tag: Fw4Tag) -> str:
    is_ignored = 1 if tag.is_ignored else 0
    mandatory_attributes = ";".join(
        byteops.to_32bit_hex_str(attr)
        for attr in (
            tag.server_id,
            tag.agent_id,
            tag.tag_id,
            tag.link_id,
            is_ignored,
            tag.sampling_exponent,
            tag.path_info,
        )
    )
    string_list = ["fw4;", mandatory_attributes]

    _encode_extensions(tag, string_list, Fw4TagKind.TRACE_STATE)
    return "".join(string_list)


def to_x_dynatrace(tag: Fw4Tag) -> str:
    mandatory_attributes = ";".join(
        byteops.to_32bit_int_str(attr)
        for attr in (
            tag.cluster_id,
            tag.server_id,
            tag.agent_id,
            tag.tag_id,
            tag.encoded_link_id,
            tag.tenant_id,
            tag.path_info,
        )
    )
    string_list = ["FW4;", mandatory_attributes]

    _encode_extensions(tag, string_list, Fw4TagKind.X_DYNATRACE)
    return "".join(string_list)
