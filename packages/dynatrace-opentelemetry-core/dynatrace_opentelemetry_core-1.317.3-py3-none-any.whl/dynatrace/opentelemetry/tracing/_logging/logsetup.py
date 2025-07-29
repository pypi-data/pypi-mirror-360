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

import collections
import logging
import os
import sys
import time
import typing

from dynatrace.opentelemetry.tracing._config.settings import (
    LogDestination,
    LogSettings,
)
from dynatrace.opentelemetry.tracing._logging.loggers import (
    get_logger_name_from,
)

ROOT_LOGGER_NAMES = ("dynatrace", "dynatraceotel")
NULL_HANDLER = logging.NullHandler()


class DelayedLogHandler(logging.NullHandler):
    def __init__(self):
        super().__init__()
        self._records = collections.deque(maxlen=100)

    def handle(self, record: logging.LogRecord) -> None:
        self._records.append(record)

    def log_delayed_records(self):
        for record in self._records:
            logger = logging.getLogger(record.name)
            if logger.isEnabledFor(record.levelno):
                logger.handle(record)
        self.clear()

    def clear(self):
        self._records.clear()


class DynatraceLogFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(
            "[Dynatrace] %(asctime)s.%(msecs)03d UTC"
            " [%(process)d-%(folded_thread_id)08x]"
            " %(levelname)-7s [%(name)-6s] %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        self.converter = time.gmtime

    @staticmethod
    def _compute_thread_id(record: logging.LogRecord):
        thread_id = record.thread or 0
        return (0xFFFFFFFF & thread_id) ^ (
            0xFFFFFFFF00000000 & thread_id
        ) >> 32

    @staticmethod
    def _get_process_id():
        if not hasattr(os, "getpid"):
            return 0
        return os.getpid()

    def formatMessage(self, record: logging.LogRecord) -> str:
        record.process = self._get_process_id()
        record.folded_thread_id = self._compute_thread_id(record)
        return super().formatMessage(record)


def _get_log_handler(log_config: LogSettings):
    if log_config.destination == LogDestination.STANDARD_OUT:
        log_handler = logging.StreamHandler(sys.stdout)
    elif log_config.destination == LogDestination.STANDARD_ERROR:
        log_handler = logging.StreamHandler(sys.stderr)
    else:
        return NULL_HANDLER

    log_handler.setFormatter(DynatraceLogFormatter())
    return log_handler


def _configure_root_loggers(log_handler: logging.Handler, log_level):
    for root_logger_name in ROOT_LOGGER_NAMES:
        logger = logging.getLogger(root_logger_name)
        logger.propagate = False
        logger.setLevel(log_level)
        logger.addHandler(log_handler)


def _configure_verbose_loggers(log_config: LogSettings):
    for log_flag in log_config.flags:
        logger = logging.getLogger(get_logger_name_from(log_flag.logger_name))
        if log_flag.enabled:
            logger.setLevel(logging.DEBUG)
        else:
            logger.addHandler(NULL_HANDLER)
            logger.propagate = False


def configure_delayed_root_loggers() -> DelayedLogHandler:
    delayed_handler = DelayedLogHandler()
    _configure_root_loggers(delayed_handler, logging.DEBUG)
    return delayed_handler


def _cleanup_delayed_handlers() -> typing.Set[DelayedLogHandler]:
    delayed_handlers = set()
    for logger_name in ROOT_LOGGER_NAMES:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            if isinstance(handler, DelayedLogHandler):
                delayed_handlers.add(handler)
    for logger_name in ROOT_LOGGER_NAMES:
        logger = logging.getLogger(logger_name)
        for delayed_handler in delayed_handlers:
            logger.removeHandler(delayed_handler)

    return delayed_handlers


def configure_loggers(log_config: LogSettings):
    delayed_handlers = _cleanup_delayed_handlers()

    log_handler = _get_log_handler(log_config)
    _configure_root_loggers(log_handler, logging.INFO)
    _configure_verbose_loggers(log_config)

    # emit delayed log messages to configured loggers
    for delayed_handler in delayed_handlers:
        delayed_handler.log_delayed_records()
