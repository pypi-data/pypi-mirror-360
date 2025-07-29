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

import abc
import errno
import json
import os
import typing
from threading import Lock

from dynatrace.opentelemetry.tracing import version
from dynatrace.opentelemetry.tracing._config import banner
from dynatrace.opentelemetry.tracing._config.settings import (
    MANDATORY_VALUE,
    ConfigAttributes,
    ConfigAttrSpec,
    DtConfig,
    is_truthy,
)
from dynatrace.opentelemetry.tracing._logging import logsetup
from dynatrace.opentelemetry.tracing._logging.loggers import core_logger

VALUE_NOT_CONFIGURED = object()
_ARRAY_DEFAULT_SEPARATOR = ":"


class ConfigProvider(abc.ABC):
    """Interface for retrieving config values for certain attributes."""

    def get_value(self, attribute: ConfigAttributes) -> typing.Any:
        attr_spec = attribute.value
        if attr_spec.is_array:
            return self._get_array_value(attr_spec)
        return self._get_value(attr_spec)

    @abc.abstractmethod
    def _get_value(self, attr_spec: ConfigAttrSpec) -> typing.Any:
        """Returns the value for the given attribute."""

    def _get_array_value(
        self, attr_spec: ConfigAttrSpec
    ) -> typing.Optional[typing.List]:
        """Returns the array value for the given attribute."""
        value = self._get_value(attr_spec)
        if value is VALUE_NOT_CONFIGURED:
            return value
        if isinstance(value, typing.List):
            return value
        if not isinstance(value, str):
            raise ValueError(f"{value} is not an array type")
        if not value:
            return []
        return value.split(_ARRAY_DEFAULT_SEPARATOR)


class CommandLineConfigProvider(ConfigProvider):
    """Provides configuration values from a command line object."""

    def __init__(self, config_object: typing.Any = None):
        self.config_object = config_object

    @staticmethod
    def _get_key(attr_spec: ConfigAttrSpec):
        key = attr_spec.to_attr_name()
        return "dt_" + key

    def _get_value(self, attr_spec: ConfigAttrSpec) -> typing.Any:
        if not self.config_object:
            return VALUE_NOT_CONFIGURED
        key = self._get_key(attr_spec)
        try:
            value = getattr(self.config_object, key)
        except AttributeError:
            return VALUE_NOT_CONFIGURED
        return value if value is not None else VALUE_NOT_CONFIGURED


class EnvironmentConfigProvider(ConfigProvider):
    """Provides configuration values from environment variables."""

    @staticmethod
    def _get_key(attr_spec: ConfigAttrSpec) -> str:
        key = attr_spec.to_attr_name()
        return "DT_" + key.upper()

    def _get_value(self, attr_spec: ConfigAttrSpec) -> typing.Any:
        key = self._get_key(attr_spec)
        value = os.getenv(key)
        if value is None:
            return VALUE_NOT_CONFIGURED
        return value


class JsonConfigProvider(ConfigProvider):
    """Provides configuration values from the JSON configuration file.

    The values are tried to be read from different location. The lookup is as
    follows:
    - try to read the file specified in the environment variable DT_CONFIG_FILE.
    - try to read the file dtconfig.json in the current working directory.
    - try to read the file dtconfig.json in the distribution's root directory.
    """

    ENV_DT_CONFIG_FILE = "DT_CONFIG_FILE"
    CONFIG_FILE_NAME = "dtconfig.json"

    def __init__(self):
        self._config_loaded = False
        self._json_config = None

    @staticmethod
    def _open_file(file_name: str):
        return open(file_name, encoding="utf-8")

    @classmethod
    def _load_json(cls, file_name: str):
        try:
            with cls._open_file(file_name) as file:
                try:
                    return json.load(file)
                except ValueError:
                    core_logger.debug(
                        "Invalid JSON configuration in %s.",
                        os.path.abspath(file_name),
                    )
                    return {}
        except OSError as ose:
            if ose.errno != errno.ENOENT:
                core_logger.debug(
                    "Error when opening configuration file: %s",
                    os.path.abspath(file_name),
                )
            return None

    @classmethod
    def _get_json_document(cls):
        document = None
        # try to load from file given by environment
        config_file = os.getenv(cls.ENV_DT_CONFIG_FILE)
        if config_file:
            document = cls._load_json(config_file)
        if document is not None:
            return document

        # try to load config from current directory
        config_file = os.path.join(os.getcwd(), cls.CONFIG_FILE_NAME)
        document = cls._load_json(config_file)
        if document is not None:
            return document

        # try to load config from distribution directory
        config_file = os.path.join(
            os.path.dirname(version.__file__), cls.CONFIG_FILE_NAME
        )
        return cls._load_json(config_file)

    def _get_or_load_config(self):
        if self._config_loaded:
            return self._json_config

        self._json_config = self._get_json_document()
        self._config_loaded = True
        return self._json_config

    @staticmethod
    def _get_key(attr_spec: ConfigAttrSpec) -> typing.Sequence[str]:
        attr_value = attr_spec.identifier
        segments = attr_value.split("/")
        key_path = []
        for segment in segments:
            path_segment = segment.replace("-", "")
            key_path.append(path_segment)
        return key_path

    def _get_value(self, attr_spec: ConfigAttrSpec) -> typing.Any:
        document = self._get_or_load_config()
        if not document:
            return VALUE_NOT_CONFIGURED

        key_path = self._get_key(attr_spec)
        current_document = document
        for segment in key_path[:-1]:
            current_document = current_document.get(segment)
            if not current_document:
                return VALUE_NOT_CONFIGURED
        return current_document.get(key_path[-1], VALUE_NOT_CONFIGURED)


class ConfigReader:
    """Reads the configuration from a list of specific sources.

    The sources and order from which configuration values are read is:
    - command line arguments
    - environment variables
    - JSON configuration file (dtconfig.json)
    """

    def __init__(self, parameters: typing.Any = None):
        self._providers = (
            CommandLineConfigProvider(parameters),
            EnvironmentConfigProvider(),
            JsonConfigProvider(),
        )

    def _convert_value(self, value, attr_spec: ConfigAttrSpec):
        if attr_spec.is_array:
            return self._convert_array(value, attr_spec)
        return self._convert_single_value(value, attr_spec)

    def _convert_single_value(self, value, attr_spec: ConfigAttrSpec):
        typed_value = self._to_typed_value(value, attr_spec)
        if attr_spec.converter is not None:
            typed_value = attr_spec.converter(typed_value)
        if typed_value is None:
            raise ValueError("None is not a valid value")
        return typed_value

    def _convert_array(
        self, array_value: typing.List, attr_spec: ConfigAttrSpec
    ) -> typing.List:
        if array_value is None:
            raise ValueError("Array must not be None")
        converted = []
        for item in array_value:
            if item is None:
                raise ValueError("Array must not contain None values")
            converted.append(self._convert_single_value(item, attr_spec))
        return converted

    @staticmethod
    def _to_typed_value(value, attr_spec: ConfigAttrSpec):
        if value is None:
            return value
        if attr_spec.value_type is bool:
            return is_truthy(value)
        if attr_spec.value_type is int:
            return int(value)
        if attr_spec.value_type is str:
            return str(value)
        raise ValueError(
            attr_spec, f"unsupported value type {attr_spec.value_type}"
        )

    def _get_value_for(self, attribute: ConfigAttributes):
        attr_spec = attribute.value
        for provider in self._providers:
            value = provider.get_value(attribute)
            if value is VALUE_NOT_CONFIGURED:
                continue
            return self._convert_value(value, attr_spec)
        if attr_spec.default is MANDATORY_VALUE:
            core_logger.warning("%s not configured", attr_spec.to_log_name())
            raise ValueError("value not configured")
        return attr_spec.default

    def _check_validation_group_attributes(
        self,
        validation_group_attributes: typing.Dict[
            str, typing.List[ConfigAttributes]
        ],
        parsed_config: typing.Dict[ConfigAttributes, typing.Any],
        invalid_attributes: typing.List[str],
    ):
        for group in validation_group_attributes:
            has_value = False
            missing_atributes = []
            for attr in validation_group_attributes[group]:
                value = self._get_value_for(attr)
                if value is not None:
                    has_value = True
                    parsed_config[attr] = value
                    break

                missing_atributes.append(f"{attr.value.to_log_name()}")

            if not has_value:
                core_logger.warning(
                    "One of the config attributes in the group %s must have a value",
                    group,
                )
                invalid_attributes.extend(missing_atributes)

    def read(self, **kwargs):
        parsed_config = {}  # type: typing.Dict[ConfigAttributes, typing.Any]
        invalid_attributes = []
        validation_group_attributes = {}  # type: typing.Dict[str, typing.List[ConfigAttributes]]
        for attr in ConfigAttributes:
            attr_spec = attr.value  # type: ConfigAttrSpec
            if not attr_spec.is_enabled:
                continue

            if attr_spec.validation_group is not None:
                group = attr_spec.validation_group
                if group not in validation_group_attributes:
                    validation_group_attributes[group] = []
                validation_group_attributes[group].append(attr)
                continue

            try:
                value = self._get_value_for(attr)
            except Exception as ex:  # pylint:disable=broad-except
                invalid_attributes.append(
                    f"{attr_spec.to_log_name()}: {str(ex)}"
                )
                value = () if attr_spec.is_array else attr_spec.value_type()

            parsed_config[attr] = value

        self._check_validation_group_attributes(
            validation_group_attributes, parsed_config, invalid_attributes
        )
        return DtConfig(parsed_config, invalid_attributes, **kwargs)


################################################################################
# globally get configuration
################################################################################

_config_lock = Lock()
_config_instance: "DtConfig" = None


def get_configuration(**kwargs) -> DtConfig:
    config = kwargs.pop("config", None)
    if isinstance(config, DtConfig):
        return config

    global _config_instance  # pylint: disable=global-statement
    if _config_instance is not None:
        return _config_instance

    with _config_lock:
        if _config_instance is not None:
            return _config_instance

        logsetup.configure_delayed_root_loggers()
        config = _read_config(**kwargs)
        logsetup.configure_loggers(config.log)

        banner.log_banner(core_logger, config)
        config.assert_is_valid()

        _config_instance = config
        return _config_instance


def _read_config(**kwargs) -> DtConfig:
    args = kwargs.pop("cmdline_args", None)
    return ConfigReader(args).read(**kwargs)
