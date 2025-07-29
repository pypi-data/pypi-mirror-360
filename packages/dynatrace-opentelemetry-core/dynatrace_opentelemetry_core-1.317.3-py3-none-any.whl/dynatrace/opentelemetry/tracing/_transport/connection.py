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
import contextlib
import functools
import http.client
import select
import socket

from dynatrace.opentelemetry.tracing._transport.exceptions import (
    ConnectTimeoutError,
    NewConnectionError,
    SSLError,
)

try:
    import ssl

    BaseSSLError = ssl.SSLError
except (ImportError, AttributeError):
    ssl = None

    class BaseSSLError(BaseException):
        pass


@contextlib.contextmanager
def _connect_error_catcher(host: str, timeout: float):
    try:
        yield
    except socket.timeout:
        raise ConnectTimeoutError(
            f"Connection to {host} timed out. (connect timeout={timeout})"
        )
    except socket.error as ex:
        raise NewConnectionError(
            f"Failed to establish a new connection to {host}: {ex}"
        )


class ConnectionCreator(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def create_connection_instance(cls, host: str, port: int, **kwargs):
        pass


class HttpConnection(http.client.HTTPConnection, ConnectionCreator):
    @classmethod
    def create_connection_instance(cls, host: str, port: int, **kwargs):
        return cls(host=host, port=port)

    def connect(self) -> None:
        with _connect_error_catcher(self.host, self.timeout):
            super().connect()


if ssl:

    def _get_cert_requirements(kwargs):
        candidate = kwargs.get("cert_reqs")
        if isinstance(candidate, str):
            attr = getattr(ssl, candidate, None)
            if attr is None:
                attr = getattr(ssl, "CERT_" + candidate)
            return attr
        return candidate

    def _get_ssl_context(kwargs):
        cert_reqs = _get_cert_requirements(kwargs)
        context = kwargs.get("ssl_context")

        if cert_reqs == ssl.CERT_NONE:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context

        return context  # passed context or None for system defaults

    class HttpsConnection(http.client.HTTPSConnection, ConnectionCreator):
        @classmethod
        def create_connection_instance(cls, host: str, port: int, **kwargs):
            context = _get_ssl_context(kwargs)
            return cls(host=host, port=port, context=context)

        def connect(self) -> None:
            with _connect_error_catcher(self.host, self.timeout):
                super().connect()

else:

    class HttpsConnection(ConnectionCreator):
        @classmethod
        def create_connection_instance(cls, host: str, port: int, **kwargs):
            raise SSLError(
                "Can't connect to HTTPS URL because the SSL module is not available."
            )


########################################################################################################################


def select_wait_for_socket(sock, read=False, write=False, timeout=None):
    if not read and not write:
        raise RuntimeError(
            "must specify at least one of read=True, write=True"
        )
    rcheck = []
    wcheck = []
    if read:
        rcheck.append(sock)
    if write:
        wcheck.append(sock)
    # When doing a non-blocking connect, most systems signal success by
    # marking the socket writable. Windows, though, signals success by marked
    # it as "exceptional". We paper over the difference by checking the write
    # sockets for both conditions. (The stdlib selectors module does the same
    # thing.)
    fn = functools.partial(select.select, rcheck, wcheck, wcheck)
    rready, wready, xready = fn(  # pylint:disable=assignment-from-no-return
        timeout
    )
    return bool(rready or wready or xready)


def poll_wait_for_socket(sock, read=False, write=False, timeout=None):
    if not read and not write:
        raise RuntimeError(
            "must specify at least one of read=True, write=True"
        )
    mask = 0
    if read:
        mask |= select.POLLIN
    if write:
        mask |= select.POLLOUT
    poll_obj = select.poll()
    poll_obj.register(sock, mask)

    # For some reason, poll() takes timeout in milliseconds
    def do_poll(timeout_sec):
        if timeout_sec is not None:
            timeout_sec *= 1000
        return poll_obj.poll(timeout_sec)

    return bool(do_poll(timeout))


def _have_working_poll():
    # Apparently some systems have a select.poll that fails as soon as you try
    # to use it, either due to strange configuration or broken monkeypatching
    # from libraries like eventlet/greenlet.
    try:
        poll_obj = select.poll()
        poll_obj.poll(0)
    except (AttributeError, OSError):
        return False

    return True


def wait_for_socket(*args, **kwargs):  # noqa: F811
    # We delay choosing which implementation to use until the first time we're
    # called. We could do it at import time, but then we might make the wrong
    # decision if someone goes wild with monkeypatching select.poll after
    # we're imported.
    global wait_for_socket  # pylint: disable=global-statement
    if _have_working_poll():
        wait_for_socket = poll_wait_for_socket
    elif hasattr(select, "select"):
        wait_for_socket = select_wait_for_socket
    return wait_for_socket(*args, **kwargs)


def wait_for_read(sock, timeout=None):
    """Waits for reading to be available on a given socket.
    Returns True if the socket is readable, or False if the timeout expired.
    """
    return wait_for_socket(sock, read=True, timeout=timeout)


_WSAENOTSOCK = 10038


def is_connection_dropped(connection):
    sock = getattr(connection, "sock", False)
    if sock is None:  # Connection already closed
        return True
    # Returns True if readable, which here means it's been dropped
    try:
        return wait_for_read(sock, timeout=0.0)
    except OSError as ex:
        # ONE-57840: On Win32, select does not work with files
        winerror = getattr(ex, "winerror", 0)
        if winerror == _WSAENOTSOCK:
            # Consider the connection dropped, it's safer to reconnect.
            # In the case of ONE-57840 where httpretty replaces the socket with
            # a temp file, the "socket" is certainly not dropped, but better
            # slow than failing.
            return True
        raise
