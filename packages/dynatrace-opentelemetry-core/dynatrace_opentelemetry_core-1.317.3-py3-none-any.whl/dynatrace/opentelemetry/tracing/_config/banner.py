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

import logging
import os
import pathlib
import platform
import socket
import sys
import time
from logging import Logger

from dynatrace._vendor.google.protobuf._version import (
    __version__ as protobuf_ver,
)
from dynatrace.odin.proto._version import __version__ as proto_ver
from dynatrace.odin.semconv._version import __version__ as semconv_ver
from dynatrace.opentelemetry.tracing import version
from dynatrace.opentelemetry.tracing._config.settings import DtConfig


def log_banner(logger: Logger, config: DtConfig):
    _log_disclaimer_if_dev_version()

    if not logger.isEnabledFor(logging.INFO):
        return

    logger.info(
        "OneAgent ODIN Python version ... %s, build date %s, SCM rev. %s",
        version.FULL_VERSION,
        version.BUILD_DATE,
        version.SCM_REVISION,
    )
    logger.info(
        "Agent library .................. %s",
        pathlib.Path(version.__file__).parent,
    )
    logger.info(
        "Runtime ........................ %s / %s / %s",
        sys.implementation.name,
        _get_py_version(),
        repr(sys.version),
    )
    logger.info(
        "Platform ....................... %s - %s",
        _get_os_type(),
        platform.platform(),
    )
    logger.info("Process ID ..................... %d", os.getpid())
    logger.info("Local timezone ................. UTC%s", time.strftime("%z"))
    logger.info("Agent host ..................... %s", socket.gethostname())
    logger.info("Protocol version ............... %s", proto_ver)
    logger.info("Semantic conventions version ... %s", semconv_ver)
    logger.info("protobuf (vendored) ............ %s", protobuf_ver)
    logger.info(
        "Cluster ID ..................... 0x%x",
        config.qualified_tenant_id.cluster_id_unsigned,
    )
    logger.info(
        "Tenant ID ...................... 0x%x",
        config.qualified_tenant_id.tenant_id_unsigned,
    )
    logger.info(
        "Tenant UUID .................... %s",
        config.qualified_tenant_id.tenant_uuid,
    )
    logger.info(
        "Agent ID ....................... 0x%x",
        config.connection.exporter_id_unsigned,
    )
    logger.info(
        "Connection URL ................. %s%s",
        config.connection.base_url,
        " (cert verification enabled)" if config.connection.verify_tls else "",
    )


def _get_py_version(vinfo=sys.implementation.version):
    return ".".join(
        map(
            str,
            (
                vinfo[:3]
                if vinfo.releaselevel == "final" and not vinfo.serial
                else vinfo
            ),
        )
    )


def _get_os_type():
    os_type = platform.system().upper()
    if os_type == "HP-UX":
        return "HPUX"
    if os_type == "SUNOS":
        return "SOLARIS"
    return os_type


def _log_disclaimer_if_dev_version():
    # pylint: disable=protected-access
    if not version.IS_DEV_VERSION:
        return

    disclaimer = (
        "[Dynatrace] This is a development version "
        f"({version.FULL_VERSION}, SCM rev. {version.SCM_REVISION})"
        " and not intended for use in production environments."
    )

    logging.warning(disclaimer)
    print(disclaimer, file=sys.stderr, flush=True)
