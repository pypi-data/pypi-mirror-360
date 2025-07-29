from typing import Callable, Dict, Optional, Set

import dynatrace.odin.semconv.v1 as semconv
from dynatrace.opentelemetry.tracing._config.settings import DtConfig
from dynatrace.opentelemetry.tracing._otel.api import AttributeValue

_AttributeMapping = Dict[str, AttributeValue]

_HEADER_FORWARDED = "forwarded"
_HEADER_FORWARDED_FOR = "x-forwarded-for"
_FORWARD_HEADER_KEYS = (_HEADER_FORWARDED, _HEADER_FORWARDED_FOR)
_HEADER_FORWARDED_PROTO = "x-forwarded-proto"
_HEADER_HOST = "host"

_HEADERS_TO_CAPTURE = {
    _HEADER_FORWARDED_PROTO: semconv.HTTP_SCHEME,
    _HEADER_HOST: semconv.HTTP_HOST,
    "user-agent": semconv.HTTP_USER_AGENT,
    "referer": semconv.DT_HTTP_REQUEST_HEADER_REFERER,
    "x-dynatrace-test": semconv.DT_HTTP_REQUEST_HEADER_X_DYNATRACE_TEST,
    "x-dynatrace-tenant": semconv.DT_HTTP_REQUEST_HEADER_X_DYNATRACE_TENANT,
}

URL_RELEVANT_HEADERS = frozenset({_HEADER_FORWARDED_PROTO, _HEADER_HOST})
EMPTY_SET = frozenset({})


def capture_headers(
    attrs: _AttributeMapping,
    get_header_value: Callable[[str], Optional[str]],
    config: DtConfig = None,
    exclude: Set[str] = EMPTY_SET,
):
    # capture required header fields
    for header_key, semconv_key in _HEADERS_TO_CAPTURE.items():
        if header_key in exclude:
            continue
        header_value = get_header_value(header_key)
        if header_value is not None:
            attrs[semconv_key] = header_value

    if config is not None:
        # capture configured client IP headers
        for client_ip_header_name in config.rum.client_ip_headers:
            client_ip_header_name = client_ip_header_name.lower()
            header_value = get_header_value(client_ip_header_name)
            if header_value is None:
                continue
            if client_ip_header_name in _FORWARD_HEADER_KEYS:
                break
            attrs[semconv.DT_RUM_CLIENTIP_HEADER_NAME] = client_ip_header_name
            attrs[f"dt.http.request.header.{client_ip_header_name}"] = (
                header_value
            )
            break

    # capture "forwarded" or "x-forwarded-for" header
    # check "forwarded" first and use "x-forwarded-for" as fallback
    forward_attr_key = semconv.DT_HTTP_REQUEST_HEADER_FORWARDED
    forward_header_value = get_header_value(_HEADER_FORWARDED)
    if forward_header_value is None:
        forward_attr_key = semconv.DT_HTTP_REQUEST_HEADER_X_FORWARDED_FOR
        forward_header_value = get_header_value(_HEADER_FORWARDED_FOR)
    if forward_header_value is not None:
        attrs[forward_attr_key] = forward_header_value
