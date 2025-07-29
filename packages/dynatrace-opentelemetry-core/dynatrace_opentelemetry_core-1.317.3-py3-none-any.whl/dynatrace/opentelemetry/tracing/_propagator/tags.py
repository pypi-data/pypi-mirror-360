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

import enum
import random
import re
from typing import Optional

from dynatrace.opentelemetry.tracing._logging.loggers import propagator_logger
from dynatrace.opentelemetry.tracing._otel.api import (
    INVALID_SPAN_ID,
    INVALID_TRACE_ID,
    SpanContext,
)
from dynatrace.opentelemetry.tracing._util.byteops import (
    int32_to_uint32,
    to_32bit_hex_str,
    to_64bit_be_hex_str,
    to_128bit_be_hex_str,
    uint32_to_int32,
)
from dynatrace.opentelemetry.tracing._util.tenant import QualifiedTenantId


def get_trace_state_key(qualified_tenant_id: QualifiedTenantId) -> str:
    return (
        to_32bit_hex_str(qualified_tenant_id.tenant_id)
        + "-"
        + to_32bit_hex_str(qualified_tenant_id.cluster_id)
        + "@dt"
    )


def _get_8bit_random_int():
    return random.getrandbits(8)


class Fw4ExtFields(enum.Enum):
    CUSTOM_BLOB = 1
    TAG_DEPTH = 2
    ENTRY_AGENT_ID = 3
    ENTRY_TAG_ID = 4
    PAYLOAD_BIT_SET = 5
    TRACE_ID = 6
    SPAN_ID = 7


class Fw4TagKind(enum.Enum):
    TRACE_STATE = 1
    X_DYNATRACE = 2


class Fw4Tag:
    MAX_BLOB_LENGTH = 0x4000
    TLV_PAYLOAD_CANARY_BIT = 0x01
    LINK_ID_IGNORED_MASK = 0x80000000
    LINK_ID_MASK = 0x07FFFFFF

    def __init__(self, span_context: Optional[SpanContext] = None):
        self.agent_id = 0
        self.cluster_id = 0
        self.tenant_id = 0

        self.server_id = 0
        self.tag_id = 0
        self.path_info = 0

        self.encoded_link_id = 0

        # extensions
        self.custom_blob = None  # type: Optional[bytes]
        self.tag_depth = 0
        self.entry_agent_id = -1
        self.entry_tag_id = -1
        self.payload_bit_set = 0
        is_ignored = False
        if span_context is not None:
            self.trace_id = span_context.trace_id
            self.span_id = span_context.span_id
            is_ignored = not span_context.trace_flags.sampled
        else:
            self.trace_id = None
            self.span_id = None
        self.set_ignored(is_ignored)

    @staticmethod
    def create_tenant_root(qualified_tenant_id: QualifiedTenantId):
        tag = Fw4Tag()
        tag.set_qualified_tenant_id(qualified_tenant_id)
        tag.generate_root_path_random()
        return tag

    @property
    def has_tag_depth(self) -> bool:
        return self.tag_depth > 0

    @property
    def has_entry_agent_id(self) -> bool:
        return self.entry_agent_id != -1

    @property
    def has_entry_tag_id(self) -> bool:
        return self.entry_tag_id >= 0

    @property
    def has_payload_bit_set(self) -> bool:
        return self.payload_bit_set != 0

    @property
    def has_trace_id(self) -> bool:
        return self.trace_id is not None and self.trace_id != INVALID_TRACE_ID

    @property
    def has_span_id(self) -> bool:
        return self.span_id is not None and self.span_id != INVALID_SPAN_ID

    def has_any_extension(self, tag_kind: Fw4TagKind):
        return (
            bool(self.custom_blob)
            or self.has_tag_depth
            or self.has_entry_agent_id
            or self.has_entry_tag_id
            or self.has_payload_bit_set
            or (self.has_trace_id and tag_kind != Fw4TagKind.TRACE_STATE)
            or self.has_span_id
        )

    def set_canary_bit(self, bit_state: bool):
        payload_bit_set = int32_to_uint32(self.payload_bit_set)
        if bit_state:
            payload_bit_set |= self.TLV_PAYLOAD_CANARY_BIT
        else:
            payload_bit_set &= ~self.TLV_PAYLOAD_CANARY_BIT
        self.payload_bit_set = uint32_to_int32(payload_bit_set)

    @property
    def link_id(self) -> int:
        encoded_link_id = int32_to_uint32(self.encoded_link_id)
        return encoded_link_id & self.LINK_ID_MASK

    def set_link_id(self, link_id: int):
        encoded_link_id = int32_to_uint32(self.encoded_link_id)
        encoded_link_id &= ~self.LINK_ID_MASK
        encoded_link_id |= link_id & self.LINK_ID_MASK
        self.encoded_link_id = uint32_to_int32(encoded_link_id)

    @property
    def sampling_exponent(self) -> int:
        encoded_link_id = int32_to_uint32(self.encoded_link_id)
        return (encoded_link_id >> 27) & 0xF

    @property
    def is_ignored(self) -> bool:
        encoded_link_id = int32_to_uint32(self.encoded_link_id)
        return (encoded_link_id & self.LINK_ID_IGNORED_MASK) != 0

    def set_ignored(self, is_ignored: bool):
        encoded_link_id = int32_to_uint32(self.encoded_link_id)
        if is_ignored:
            encoded_link_id |= self.LINK_ID_IGNORED_MASK
        else:
            encoded_link_id &= ~self.LINK_ID_IGNORED_MASK
        self.encoded_link_id = uint32_to_int32(encoded_link_id)

    @property
    def root_path_random(self) -> int:
        path_info = int32_to_uint32(self.path_info)
        return path_info & 0xFF

    def generate_root_path_random(self):
        self._set_root_path_random(_get_8bit_random_int())

    def _set_root_path_random(self, root_path_random: int):
        path_info = int32_to_uint32(self.path_info)
        path_info &= 0xFFFFFF00
        path_info |= root_path_random
        self.path_info = uint32_to_int32(path_info)

    @property
    def max_sampling_exponent(self) -> int:
        path_info = int32_to_uint32(self.path_info)
        return (path_info >> 8) & 0xFF

    @property
    def path_info_reserved(self) -> int:
        path_info = int32_to_uint32(self.path_info)
        return (path_info >> 16) & 0xFFFFFF

    def set_qualified_tenant_id(self, qualified_tenant_id: QualifiedTenantId):
        self.cluster_id = qualified_tenant_id.cluster_id
        self.tenant_id = qualified_tenant_id.tenant_id

    def propagate(self, span_context: SpanContext):
        tag = Fw4Tag(span_context)
        tag.cluster_id = self.cluster_id
        tag.tenant_id = self.tenant_id
        tag.encoded_link_id = self.encoded_link_id
        tag.set_link_id(0)
        tag.server_id = self.server_id
        tag.path_info = self.path_info
        tag.custom_blob = self.custom_blob
        tag.tag_depth = self.tag_depth + 1
        tag.entry_agent_id = self.entry_agent_id
        tag.entry_tag_id = self.entry_tag_id
        tag.payload_bit_set = 0
        return tag

    def __repr__(self) -> str:
        tag_prefix = (
            "FW4("
            "{self.cluster_id}"
            ";{self.server_id}"
            ";{self.agent_id}"
            ";{self.tag_id}"
            ";{self.link_id}:{ignored}:{self.sampling_exponent}"
            ";{self.tenant_id}"
            ";{self.root_path_random}"
            ";{self.max_sampling_exponent}"
            ";{self.path_info_reserved}".format(
                self=self, ignored="I" if self.is_ignored else "S"
            )
        )

        variable_params = [tag_prefix]
        if self.custom_blob is not None:
            variable_params.append(";B:")
            variable_params.append(self.custom_blob.hex())
        if self.tag_depth != 0:
            variable_params.append(";d:")
            variable_params.append(hex(self.tag_depth))
        if self.entry_agent_id != 0:
            variable_params.append(";a:")
            variable_params.append(format(self.entry_agent_id, "x"))
        if self.entry_tag_id != 0:
            variable_params.append(";t:")
            variable_params.append(hex(self.entry_tag_id))
        if self.payload_bit_set != 0:
            variable_params.append(";p:")
            variable_params.append(hex(self.payload_bit_set))
        if self.trace_id is not None:
            variable_params.append(";T:")
            variable_params.append(to_128bit_be_hex_str(self.trace_id))
        if self.span_id is not None:
            variable_params.append(";S:")
            variable_params.append(to_64bit_be_hex_str(self.span_id))
        variable_params.append(")")

        return "".join(variable_params)


_MT_PREFIX = "MT_3_"
_XDTC_PREFIX = 'sn="v_4_'
_XDTC_KEY_OR_VAL = "[a-zA-Z0-9-]+"
_XDTC_KEY_VAL_PAIR = _XDTC_KEY_OR_VAL + "_" + _XDTC_KEY_OR_VAL
_XDTC_REGEX = re.compile(
    '^sn="v_4_(?:' + _XDTC_KEY_VAL_PAIR + "_)*?"
    "srv_(" + _XDTC_KEY_OR_VAL + ")(?:_" + _XDTC_KEY_OR_VAL + ')*"'
)


class RumTag:
    def __init__(
        self,
        server_id: int,
        mobile_tag: str = None,
        xdtc_header: str = None,
        rum_app_id: str = None,
    ):
        self.server_id = server_id
        self.mobile_tag = mobile_tag
        self.xdtc_header = xdtc_header
        self.rum_app_id = rum_app_id

    @staticmethod
    def from_mobile_tag(mobile_tag: str) -> Optional["RumTag"]:
        """Returns a RUM tag instance if the given mobile tag is valid and a
        server ID could be extracted.

        The tag string is expected to be in version 3 in the format:
        MT_<version>_<serverID>_<visitorID>_<sessionNr>_<appID>_<actionID>_<threadID>_<requestID>
        """
        if (
            not mobile_tag
            or len(mobile_tag) < 18  # MT prefix + 8 * ('_' + digit)
            or not mobile_tag.startswith(_MT_PREFIX)
        ):
            return None

        try:
            start_idx = len(_MT_PREFIX)
            end_idx = mobile_tag.find("_", start_idx)
            if end_idx < 0:
                propagator_logger.debug(
                    "Mobile tag did not contain a server ID: %s", mobile_tag
                )
                return None

            server_id = int(mobile_tag[start_idx:end_idx])
            return RumTag(server_id, mobile_tag)
        except ValueError:
            propagator_logger.debug(
                "Unparsable server ID in mobile tag: %s", mobile_tag
            )
            return None

    @classmethod
    def from_xdtc_header(
        cls, xdtc_header: str, rum_app_id: Optional[str]
    ) -> Optional["RumTag"]:
        """Returns a RumTag if the server ID could be parsed from the given
        x-dtc header.

        x-dtc format: sn="<session-state>", pc="<page-context>", v="<visitor-id>", r="<referer>"
        server ID is inside session-state
        session-state format: v_4_key1_value1_key2_value2...
        key for server ID is "srv"
        """
        if not xdtc_header or not xdtc_header.startswith(_XDTC_PREFIX):
            return None
        match = _XDTC_REGEX.match(xdtc_header)
        if not match:
            propagator_logger.debug(
                "Invalid xdtc-header or missing srv field."
            )
            return None

        server_id_match = match.group(1)
        try:
            if server_id_match.startswith("-"):
                if not server_id_match.startswith("-2D"):
                    propagator_logger.debug(
                        "Incorrectly encoded server ID in xdtc-header: %s",
                        server_id_match,
                    )
                    return None
                server_id_match = "-" + server_id_match[3:]

            server_id = int(server_id_match)
            return RumTag(
                server_id, xdtc_header=xdtc_header, rum_app_id=rum_app_id
            )
        except ValueError:
            propagator_logger.debug(
                "Unparsable integer in x-dtc server ID: %s", server_id_match
            )
            return None

    def __repr__(self):
        return (
            "RumTag("
            "server_id={self.server_id}, "
            "mt='{self.mobile_tag}', "
            "xdtc='{self.xdtc_header}', "
            "app_id='{self.rum_app_id}'"
            ")"
        ).format(self=self)
