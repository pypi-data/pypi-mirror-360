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
import os
import random
import re
from typing import Any, Callable, Dict, List, Type, Union
from urllib.parse import urlparse

from dynatrace.opentelemetry.tracing import version
from dynatrace.opentelemetry.tracing._logging.loggers import core_logger
from dynatrace.opentelemetry.tracing._util.tenant import QualifiedTenantId

ReadValueType = Union[int, bool, str]

_TENANT_VALIDATION_PATTERN = re.compile("[a-zA-Z0-9-]+")


def is_truthy(value: Union[str, bool, None]) -> bool:
    if isinstance(value, bool):
        return value
    if not value or not isinstance(value, str):
        return False
    return value.lower().strip() not in ("0", "false")


def _generate_exporter_id() -> int:
    exporter_id = random.getrandbits(64)
    if exporter_id >= 2**63:
        return exporter_id - 2**64
    return exporter_id


################################################################################
# Refined config types
################################################################################


class LogDestination(enum.Enum):
    """Defines the destination to which logs are reported."""

    OFF = 1
    """No log messages are reported. This is the default value"""
    STANDARD_OUT = 2
    """Log messages are reported to the standard out stream."""
    STANDARD_ERROR = 3
    """Log messages are reported to the standard error stream."""

    @staticmethod
    def from_cfg_str(value: str) -> "LogDestination":
        if not value:
            return LogDestination.OFF
        value = value.lower()
        if value == "stdout":
            return LogDestination.STANDARD_OUT
        if value == "stderr":
            return LogDestination.STANDARD_ERROR
        return LogDestination.OFF


class LoggerFlag:
    def __init__(self, logger_name: str, enabled: bool):
        self.logger_name = logger_name
        self.enabled = enabled

    @classmethod
    def flags_from_cfg_str(cls, flags: str) -> List["LoggerFlag"]:
        logger_flags = []
        if not flags:
            return logger_flags

        for flag in flags.split(","):
            flag_tuple = flag.split("=")
            if len(flag_tuple) != 2:
                continue
            logger_flags.append(
                cls(flag_tuple[0].strip(), is_truthy(flag_tuple[1]))
            )
        return logger_flags


def _validate_tenant_uuid(tenant_uuid: str) -> str:
    if tenant_uuid is None or not _TENANT_VALIDATION_PATTERN.fullmatch(
        tenant_uuid
    ):
        raise ValueError(f"invalid value '{tenant_uuid}'")
    return tenant_uuid


def _validate_positive_value(value: int) -> int:
    if value <= 0:
        raise ValueError(
            f"invalid value '{value}'. Positive integer was expected."
        )
    return value


################################################################################
# Config definition
################################################################################
MANDATORY_VALUE = object()


class ConfigAttrSpec:
    def __init__(
        self,
        identifier: str,
        value_type: Type[ReadValueType],
        default: Any = None,
        converter: Callable[[ReadValueType], Any] = None,
        is_array: bool = False,
        is_enabled: bool = True,
        validation_group: str = None,
    ):
        """Specifies how to read an attribute from the configuration

        Args:
            identifier: the identifier of the config attribute. Every config
                mechanism (cmd-line, env-vars, JSON) uses the identifier as base
                to determine the attribute name.
            value_type: the type of the value how it is read from the underlying
                config.
            default: the default value if the attribute is not configured.
            converter: a callable that is applied to the value read from the
                config, e.g. to convert the value into a more specific type.
                for array attributes the converter is applied to every
                element in the array.
            is_array: indicator whether the config attribute is an array or not
            is_enabled: indicator whether the config attribute should be read or
                not.
        """
        self.identifier = identifier
        self.converter = converter
        self.value_type = value_type
        self.is_array = is_array
        self.is_enabled = is_enabled
        self.default = () if default is None and self.is_array else default
        self.validation_group = validation_group

    def to_attr_name(self) -> str:
        key = self.identifier
        for separator in ("/", "-"):
            key = key.replace(separator, "_")
        return key.lower()

    def to_log_name(self):
        key = self.identifier.replace("/", ".")
        key = key.replace("-", "")
        return key


class ConfigAttrSensorEnableSpec(ConfigAttrSpec):
    def __init__(
        self, identifier: str, dist_entry_point_name: str, default: bool = True
    ):
        super().__init__(identifier, bool, default=default)
        self.distribution_entry_point_name = dist_entry_point_name


class ConfigAttributes(enum.Enum):
    AGENT_ACTIVE = ConfigAttrSpec("Agent-Active", bool, is_enabled=False)

    CLUSTER_ID = ConfigAttrSpec("Cluster-ID", int, MANDATORY_VALUE)
    TENANT = ConfigAttrSpec(
        "Tenant", str, MANDATORY_VALUE, converter=_validate_tenant_uuid
    )

    CONNECTION_BASE_URL = ConfigAttrSpec(
        "Connection/Base-Url", str, MANDATORY_VALUE
    )
    CONNECTION_AUTH_TOKEN = ConfigAttrSpec(
        "Connection/Auth-Token", str, validation_group="Auth-Token"
    )
    CONNECTION_AUTH_TOKEN_SECRETS_MANAGER_ARN = ConfigAttrSpec(
        "Connection/Auth-Token-Secrets-Manager-Arn",
        str,
        validation_group="Auth-Token",
    )
    CONNECTION_PROXY = ConfigAttrSpec(
        "Connection/Proxy", str, is_enabled=False
    )
    CONNECTION_CERTIFICATES = ConfigAttrSpec(
        "Connection/Certificates", str, is_enabled=False
    )
    CONNECTION_DISABLE_CERTIFICATE_CHECK = ConfigAttrSpec(
        "Connection/Insecure-Disable-Certificate-Check", bool
    )
    CONNECTION_FLUSH_CONNECT_TIMEOUT_MS = ConfigAttrSpec(
        "Connection/Flush-Connect-Timeout-Ms",
        int,
        converter=_validate_positive_value,
        default=500,
    )
    CONNECTION_FLUSH_DATA_TIMEOUT_MS = ConfigAttrSpec(
        "Connection/Flush-Data-Timeout-Ms",
        int,
        converter=_validate_positive_value,
        default=2000,
    )

    RUM_APPLICATION_ID = ConfigAttrSpec("RUM/Application-Id", str)
    RUM_CLIENT_IP_HEADERS = ConfigAttrSpec(
        "RUM/Client-Ip-Headers", str, converter=str.lower, is_array=True
    )

    LOGGING_DESTINATION = ConfigAttrSpec(
        "Logging/Destination",
        str,
        LogDestination.OFF,
        converter=LogDestination.from_cfg_str,
    )
    LOGGING_FLAGS = ConfigAttrSpec(
        "Logging/Python/Flags",
        str,
        (),
        converter=LoggerFlag.flags_from_cfg_str,
    )

    TESTABILITY_SPAN_PROCESSING_INTERVAL = ConfigAttrSpec(
        "Testability/Span-Processing-Interval-Ms", int
    )
    TESTABILITY_KEEP_ALIVE_INTERVAL = ConfigAttrSpec(
        "Testability/Keep-Alive-Interval-Ms", int
    )

    OTEL_ALLOW_EXPLICIT_PARENT = ConfigAttrSpec(
        "Open-Telemetry/Allow-Explicit-Parent", bool, default=False
    )
    OTEL_DISABLED_SENSORS = ConfigAttrSpec(
        "Open-Telemetry/Disabled-Sensors", str, is_array=True
    )
    OTEL_ENABLE_INTEGRATION = ConfigAttrSpec(
        "Open-Telemetry/Enable-Integration", bool, default=False
    )
    OTEL_OVERRIDE_MAX_API_VERSION = ConfigAttrSpec(
        "Open-Telemetry/Override-Max-Api-Version", str
    )
    ENABLE_LAMBDA_EXTENSION_REGISTRATION = ConfigAttrSpec(
        "Enable-Lambda-Extension-Registration", bool, default=True
    )

    DEBUG_ADD_STACK_ON_START = ConfigAttrSpec(
        "Debug/Add-Stack-On-Start", bool, default=False
    )

    SENSORS_ENABLE_AIOHTTP_CLIENT = ConfigAttrSensorEnableSpec(
        "Sensors/Enable/Aiohttp-Client", "aiohttp-client"
    )
    SENSORS_ENABLE_AWS_SDK = ConfigAttrSensorEnableSpec(
        "Sensors/Enable/Aws-Sdk", "aws-lambda-out"
    )
    SENSORS_ENABLE_FLASK = ConfigAttrSensorEnableSpec(
        "Sensors/Enable/Flask", "flask"
    )
    SENSORS_ENABLE_HTTP_CLIENT = ConfigAttrSensorEnableSpec(
        "Sensors/Enable/Http-Client", "http_client"
    )
    SENSORS_ENABLE_REDIS = ConfigAttrSensorEnableSpec(
        "Sensors/Enable/Redis", "redis"
    )
    SENSORS_ENABLE_REQUESTS = ConfigAttrSensorEnableSpec(
        "Sensors/Enable/Requests", "requests"
    )
    SENSORS_ENABLE_URLLIB3 = ConfigAttrSensorEnableSpec(
        "Sensors/Enable/Urllib3", "urllib3"
    )


class CommandLineConfig:
    """Holds all configuration attributes in the form as they are expected to be
    passed form the command line."""

    def __init__(self, **kwargs):
        """Create a new CommandLineConfig instance

        Args:
            cluster_id: the Cluster ID to configure
            tenant: the Tenant UUID to configure
            connection_base_url: the Base URL to where the exporter should connect
            connection_auth_token: the token to be used for authentication
            connection_insecure_disable_certificate_check: config to verify SSL
                connection
            rum_application_id: the RUM application ID to be used
            rum_client_ip_headers: the client IP headers to extract for RUM
            logging_destination: the destination to where to log to
            logging_python_flags: config to activate debug logging
            testability_span_processing_interval_ms: config for export interval
            testability_keep_alive_interval_ms: config for keep alive message
                interval
            enable_lambda_extension_registration: config to enable/disable fast
                response
            open_telemetry_disabled_sensors: config for suppressed OTEL sensors
        """
        for attr in ConfigAttributes:
            name = attr.value.to_attr_name()
            value = kwargs.get(name)
            setattr(self, "dt_" + name, value)


################################################################################
# Settings
################################################################################


class ConnectionSettings:
    """Provides connection related configuration."""

    BASE_URL_SUFFIX = "odin/v1"
    SPAN_URL_SUFFIX = BASE_URL_SUFFIX + "/spans"

    def __init__(
        self,
        config: Dict[ConfigAttributes, Any],
        invalid_attributes: List[str],
    ):
        base_url = config.get(ConfigAttributes.CONNECTION_BASE_URL)
        if not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url
        self.span_endpoint_url = base_url + self.SPAN_URL_SUFFIX

        self.auth_token = config.get(ConfigAttributes.CONNECTION_AUTH_TOKEN)
        self.auth_token_secrets_manager_arn = config.get(
            ConfigAttributes.CONNECTION_AUTH_TOKEN_SECRETS_MANAGER_ARN
        )

        self.flush_connect_timeout_millis = config.get(
            ConfigAttributes.CONNECTION_FLUSH_CONNECT_TIMEOUT_MS
        )
        self.flush_data_timeout_millis = config.get(
            ConfigAttributes.CONNECTION_FLUSH_DATA_TIMEOUT_MS
        )

        self.verify_tls = _needs_tls_verification(
            self.span_endpoint_url, config, invalid_attributes
        )
        self.exporter_id = _generate_exporter_id()
        self.exporter_id_unsigned = self.exporter_id & (2**64 - 1)


def _needs_tls_verification(
    url: str,
    config: Dict[ConfigAttributes, Any],
    invalid_attributes: List[str],
) -> bool:
    attr = ConfigAttributes.CONNECTION_DISABLE_CERTIFICATE_CHECK
    disable_cert_check = config.get(attr)

    verify_tls = (
        version.IS_PACKAGE_MODE
        if disable_cert_check is None
        else not disable_cert_check
    )

    host_part = urlparse(url).netloc.lower()
    is_tls_checked_domain = (
        ".dynatrace.com" in host_part
        or ".dynatracelabs.com" in host_part
        or ".ruxit.com" in host_part
        or ".ruxitlabs.com" in host_part
    )

    if not is_tls_checked_domain:
        return verify_tls

    if version.IS_PACKAGE_MODE and not verify_tls:
        # compile-time packages raise an error when deactivating for a DT domain
        invalid_attributes.append(
            f"{attr.value.to_log_name()}: Certificate validation must not be"
            f"disabled when connecting to a Dynatrace domain ({host_part})."
        )
    elif disable_cert_check is True:
        # explicitly configured to 'False' (i.e. not None)
        core_logger.warning(
            "%s: Ignoring config. Certificate validation for a Dynatrace domain"
            " (%s) cannot be disabled ",
            attr.value.to_log_name(),
            host_part,
        )
    return True


class RumSettings:
    """Provides RUM configuration"""

    def __init__(self, config: Dict[ConfigAttributes, Any]):
        self.application_id = config.get(ConfigAttributes.RUM_APPLICATION_ID)
        self.client_ip_headers = config.get(
            ConfigAttributes.RUM_CLIENT_IP_HEADERS
        )


class LogSettings:
    """Provides log related configuration."""

    DEFAULT_DESTINATION = LogDestination.OFF

    def __init__(self, config: Dict[ConfigAttributes, Any]):
        self.destination = config.get(ConfigAttributes.LOGGING_DESTINATION)
        self.flags = config.get(ConfigAttributes.LOGGING_FLAGS)


class OTelSettings:
    """Provides OpenTelemetry settings."""

    def __init__(self, config: Dict[ConfigAttributes, Any]):
        disabled_sensors = config.get(ConfigAttributes.OTEL_DISABLED_SENSORS)
        self._disabled_sensors_matcher = re.compile(
            "|".join(
                re.escape(s[:-1]) + ".*" if s.endswith("*") else re.escape(s)
                for s in disabled_sensors
            )
        ).fullmatch

        self.allow_explicit_parent = config.get(
            ConfigAttributes.OTEL_ALLOW_EXPLICIT_PARENT
        )
        self.enable_integration = config.get(
            ConfigAttributes.OTEL_ENABLE_INTEGRATION
        )
        self.override_max_api_version = config.get(
            ConfigAttributes.OTEL_OVERRIDE_MAX_API_VERSION
        )

    def is_disabled_sensor(self, libname):
        return bool(self._disabled_sensors_matcher(libname))


class DebugSettings:
    """Provides debug settings."""

    def __init__(self, config: Dict[ConfigAttributes, Any]):
        self.add_stack_on_start = config.get(
            ConfigAttributes.DEBUG_ADD_STACK_ON_START
        )


class EnvResources:
    def __init__(self):
        self.tags = os.environ.get("DT_TAGS")
        self.custom_prop = os.environ.get("DT_CUSTOM_PROP")


class SensorSettings:
    def __init__(self, config: Dict[ConfigAttributes, Any]):
        self._enabled = {
            attr.value.distribution_entry_point_name: config.get(attr)
            for attr in config
            if isinstance(attr.value, ConfigAttrSensorEnableSpec)
        }

    def is_enabled(self, name: str) -> bool:
        return self._enabled.get(name, False)

    def is_known(self, name) -> bool:
        return name in self._enabled


class ExtraSettings:
    """Holds additional programmatic settings not read from configurations."""

    DEFAULT_REPORT_INTERVAL_MILLIS = 3000
    DEFAULT_KEEP_ALIVE_INTERVAL_MILLIS = 25000
    DEFAULT_MAX_WATCHLIST_SIZE = 2048
    DEFAULT_MAX_SPAN_AGE_MILLIS = 115 * 60 * 1000  # 1h 55mins (in millis)
    DEFAULT_REGULAR_EXPORT_TIMEOUTS_MILLIS = (10000, 60000)
    DEFAULT_RETRY_TIMEOUTS_MILLIS = ((5000, 1000), (15000, 3000))

    def __init__(self, config: Dict[ConfigAttributes, Any], **kwargs):
        """Creates a new ExtraSettings instance

        Args:
            config: parsed configuration attributes
            report_interval_millis: The interval in milliseconds in which the span
                processor should run exports to the backend.
            keep_alive_interval_millis: The interval in milliseconds in which the
                span processor should send keep alive messages for spans. This value
                should be a multiple of report_interval_millis.
            max_watchlist_size: The maximum number of spans which the span processor
                keeps watching simultaneously. New spans will be dropped if the
                current number of watched spans exceeds this parameter.
            max_span_age_millis: The time maximum time in millis to keep unended
                spans in the watchlist
            regular_export_timeouts_millis: A tuple in the form of
                (connection_timeout, read_timeout) used by the exporter for regular
                export operations. Values are expected in milliseconds.
            retry_timeouts_millis: A sequence of tuples consisting of timeout and
                jitter in milliseconds. In case of an export error, the exporter
                will use the given timeouts for retrying. A tuple in the given
                sequence is in the form of (timeout, jitter). This means the
                exporter will wait timeout +/- rnd(jitter) between retry attempts
        """
        # span processor settings
        span_processing_interval = config.get(
            ConfigAttributes.TESTABILITY_SPAN_PROCESSING_INTERVAL
        )
        if span_processing_interval is not None:
            kwargs["report_interval_millis"] = span_processing_interval
        self.report_interval_millis = kwargs.get(
            "report_interval_millis", self.DEFAULT_REPORT_INTERVAL_MILLIS
        )

        keep_alive_interval = config.get(
            ConfigAttributes.TESTABILITY_KEEP_ALIVE_INTERVAL
        )
        if keep_alive_interval is not None:
            kwargs["keep_alive_interval_millis"] = keep_alive_interval
        self.keep_alive_interval_millis = kwargs.get(
            "keep_alive_interval_millis",
            self.DEFAULT_KEEP_ALIVE_INTERVAL_MILLIS,
        )
        self.max_watchlist_size = kwargs.get(
            "max_watchlist_size", self.DEFAULT_MAX_WATCHLIST_SIZE
        )
        self.max_span_age_millis = kwargs.get(
            "max_span_age_millis", self.DEFAULT_MAX_SPAN_AGE_MILLIS
        )

        # exporter settings
        self.regular_send_timeouts_millis = kwargs.get(
            "regular_export_timeouts_millis",
            self.DEFAULT_REGULAR_EXPORT_TIMEOUTS_MILLIS,
        )
        self.retry_timeouts_millis = kwargs.get(
            "retry_timeouts_millis", self.DEFAULT_RETRY_TIMEOUTS_MILLIS
        )


class DtConfig:
    """Provides the whole tracing specific configuration."""

    def __init__(
        self,
        config: Dict[ConfigAttributes, Any],
        invalid_attributes: List[str],
        **kwargs,
    ):
        self._invalid_attributes = invalid_attributes
        cluster_id = config.get(ConfigAttributes.CLUSTER_ID)
        tenant_uuid = config.get(ConfigAttributes.TENANT)
        self.qualified_tenant_id = QualifiedTenantId(
            cluster_id=cluster_id, tenant_uuid=tenant_uuid
        )
        self.enable_lambda_extension_registration = config.get(
            ConfigAttributes.ENABLE_LAMBDA_EXTENSION_REGISTRATION
        )

        self.sensors = SensorSettings(config)
        self.connection = ConnectionSettings(config, invalid_attributes)
        self.rum = RumSettings(config)
        self.log = LogSettings(config)
        self.otel = OTelSettings(config)
        self.debug = DebugSettings(config)
        self.extra = ExtraSettings(config, **kwargs)
        self.env_resources = EnvResources()

    def assert_is_valid(self):
        if not self._invalid_attributes:
            return
        raise ValueError(
            "Invalid configuration: "
            f"The following fields are missing or invalid: {self._invalid_attributes}"
        )
