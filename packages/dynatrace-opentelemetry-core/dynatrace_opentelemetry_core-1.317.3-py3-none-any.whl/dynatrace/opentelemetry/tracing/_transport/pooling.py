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

import errno
import http.client
import queue
import socket
import typing
import urllib.parse

from dynatrace.opentelemetry.tracing._transport import exceptions
from dynatrace.opentelemetry.tracing._transport.connection import (
    BaseSSLError,
    HttpConnection,
    HttpsConnection,
    is_connection_dropped,
)
from dynatrace.opentelemetry.tracing._transport.response import HttpResponse
from dynatrace.opentelemetry.tracing._transport.timeout import (
    DEFAULT_TIMEOUT,
    Timeout,
)

BodyT = typing.Union[bytes, str]  # pylint: disable=invalid-name
HeadersT = typing.Mapping[str, str]  # pylint: disable=invalid-name
ConnectionT = typing.Union[  # pylint: disable=invalid-name
    HttpConnection, HttpsConnection
]

_SCHEME_TO_CONNECTION = {"http": HttpConnection, "https": HttpsConnection}
_SCHEME_TO_DEFAULT_PORT = {"http": 80, "https": 443}

# This is taken from http://hg.python.org/cpython/file/7aaba721ebc0/Lib/socket.py#l252
_blocking_errnos = {errno.EAGAIN, errno.EWOULDBLOCK}


def _scheme_from_parsed_url(parsed_url) -> str:
    return (parsed_url.scheme or "http").lower()


def _hostname_from_parsed_url(parsed_url) -> typing.Optional[str]:
    hostname = parsed_url.hostname
    if hostname:
        hostname = hostname.lower()
    return hostname


def _port_from_parsed_url(parsed_url, scheme: str) -> int:
    return parsed_url.port or _SCHEME_TO_DEFAULT_PORT[scheme]


def _get_pool_timeout(
    pool_timeout: typing.Optional[float], timeout: Timeout
) -> typing.Optional[float]:
    if pool_timeout is not None:
        return pool_timeout
    return timeout.total


class PooledConnection:
    def __init__(self, base_url: str, max_size=1, block=True, **conn_kw_args):
        parsed_url = urllib.parse.urlparse(base_url)
        self._scheme = _scheme_from_parsed_url(parsed_url)
        if self._scheme not in _SCHEME_TO_CONNECTION:
            raise exceptions.LocationValueError(
                f"Scheme '{self._scheme}' of URL '{base_url}' not supported"
            )

        self._host = _hostname_from_parsed_url(parsed_url)
        if not self._host:
            raise exceptions.LocationValueError(
                f"No host specified in '{base_url}'"
            )
        self._host = self._host.lower()
        self._port = _port_from_parsed_url(parsed_url, self._scheme)

        self._pool = queue.LifoQueue(maxsize=max_size)
        for _ in range(max_size):
            self._pool.put(None)

        self._block = block
        self._connection_class = _SCHEME_TO_CONNECTION[self._scheme]
        self._conn_kw_args = conn_kw_args

    def _prepare_url_path(self, url: str) -> str:
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.hostname:
            # relative url path
            return url if url.startswith("/") else "/" + url
        self._assert_same_host(parsed_url)
        path = parsed_url.path
        if not path.startswith("/"):
            path = "/" + path

        if parsed_url.query:
            path += "?" + parsed_url.query
        return path

    def _assert_same_host(self, parsed_url):
        scheme = _scheme_from_parsed_url(parsed_url)
        host = _hostname_from_parsed_url(parsed_url)
        port = _port_from_parsed_url(parsed_url, scheme)
        if (scheme, host, port) != (self._scheme, self._host, self._port):
            raise exceptions.HostChangedError(
                "Trying to connect to different host: "
                f"{scheme}://{host}:{port} != "
                f"{self._scheme}://{self._host}:{self._port}"
            )

    def post(
        self,
        url: str,
        headers: HeadersT = None,
        body: BodyT = None,
        timeout: Timeout = DEFAULT_TIMEOUT,
        pool_timeout: float = None,
    ):
        return self.request(
            "POST",
            url,
            headers=headers,
            body=body,
            timeout=timeout,
            pool_timeout=pool_timeout,
        )

    def request(
        self,
        method: str,
        url: str,
        headers: HeadersT = None,
        body: BodyT = None,
        timeout: Timeout = DEFAULT_TIMEOUT,
        pool_timeout: float = None,
    ) -> HttpResponse:
        url_path = self._prepare_url_path(url)
        pool_timeout = _get_pool_timeout(pool_timeout, timeout)

        conn = None
        clean_exit = False
        release_conn = True
        try:
            conn = self._get_connection(pool_timeout)

            httplib_response = self._make_request(
                conn,
                method,
                url_path,
                timeout=timeout,
                body=body,
                headers=headers,
            )

            response = HttpResponse(httplib_response)
            clean_exit = True
            return response
        except exceptions.EmptyPoolError:
            clean_exit = True
            release_conn = False
            raise
        except (
            exceptions.TimeoutError,
            http.client.HTTPException,
            socket.error,
            exceptions.ProtocolError,
            BaseSSLError,
            exceptions.SSLError,
        ) as ex:
            if isinstance(ex, BaseSSLError):
                raise exceptions.SSLError(ex)
            if isinstance(ex, (socket.error, http.client.HTTPException)):
                excls = exceptions.ProtocolError
                if isinstance(
                    ex, (http.client.RemoteDisconnected, ConnectionResetError)
                ):
                    excls = exceptions.RemoteDisconnected
                raise excls("Connection aborted", ex)
            raise
        finally:
            if not clean_exit:
                conn = conn and conn.close()
                release_conn = True

            if release_conn:
                self._put_connection(conn)

    def _make_request(
        self,
        conn: ConnectionT,
        method: str,
        url: str,
        headers: HeadersT,
        body: BodyT,
        timeout: Timeout,
    ) -> http.client.HTTPResponse:
        self._set_connection_connect_timeout(conn, timeout)
        try:
            headers = headers if headers is not None else {}
            conn.request(method, url, headers=headers, body=body)
        except BrokenPipeError:
            # We are swallowing BrokenPipeError (errno.EPIPE) since the server is
            # legitimately able to close the connection after sending a valid response.
            # With this behaviour, the received response is still readable.
            pass
        except IOError as ex:
            # MacOS/Linux
            # EPROTOTYPE is needed on macOS
            # https://erickt.github.io/blog/2014/11/19/adventures-in-debugging-a-potential-osx-kernel-bug/
            if ex.errno != errno.EPROTOTYPE:
                raise

        self._set_connection_read_timeout(conn, timeout)

        try:
            httplib_response = conn.getresponse()
        except (socket.timeout, BaseSSLError, socket.error) as ex:
            self._raise_timeout(ex, timeout.read_timeout)
            raise ex
        return httplib_response

    @staticmethod
    def _set_connection_connect_timeout(conn: ConnectionT, timeout: Timeout):
        connect_timeout = timeout.connect_timeout
        if connect_timeout is None:
            # pylint: disable=protected-access
            conn.timeout = socket._GLOBAL_DEFAULT_TIMEOUT
        else:
            conn.timeout = connect_timeout

    @staticmethod
    def _set_connection_read_timeout(conn: ConnectionT, timeout: Timeout):
        if not conn.sock:
            return
        read_timeout = timeout.read_timeout
        # In Python 3 socket.py will catch EAGAIN and return None when you
        # try and read into the file pointer created by http.client, which
        # instead raises a BadStatusLine exception. Instead of catching
        # the exception and assuming all BadStatusLine exceptions are read
        # timeouts, check for a zero timeout before making the request.
        if read_timeout == 0:
            raise exceptions.ReadTimeoutError(
                f"Read timed out. (read timeout={read_timeout})"
            )
        if read_timeout is None:
            conn.sock.settimeout(socket.getdefaulttimeout())
        else:
            conn.sock.settimeout(read_timeout)

    @staticmethod
    def _raise_timeout(err: Exception, timeout_value: float):
        """Is the error actually a timeout? Will raise a ReadTimeout or pass"""

        if isinstance(err, socket.timeout):
            raise exceptions.ReadTimeoutError(
                f"Read timed out. (read timeout={timeout_value})"
            )

        # See the above comment about EAGAIN in Python 3.
        if hasattr(err, "errno") and err.errno in _blocking_errnos:
            raise exceptions.ReadTimeoutError(
                f"Read timed out. (read timeout={timeout_value})"
            )

    def _get_connection(self, pool_timeout: float):
        conn = None
        try:
            conn = self._pool.get(block=self._block, timeout=pool_timeout)
        except AttributeError:
            raise exceptions.ClosedPoolError("Pool is closed.")
        except queue.Empty:
            if self._block:
                raise exceptions.EmptyPoolError(
                    "Pool reached maximum size and no more connections are allowed."
                )

        if conn and is_connection_dropped(conn):
            conn.close()
        return conn or self._new_connection()

    def _new_connection(self) -> ConnectionT:
        conn = self._connection_class.create_connection_instance(
            host=self._host,
            port=self._port,
            **self._conn_kw_args,  # additional args ssl_context, cert_reqs, ...
        )
        return conn

    def _put_connection(self, conn: ConnectionT):
        try:
            self._pool.put(conn, block=False)
            return
        except AttributeError:
            pass  # pool closed
        except queue.Full:
            pass

        if conn:  # was not put back into the pool so close it
            conn.close()

    def close(self):
        if self._pool is None:
            return

        old_pool, self._pool = self._pool, None
        try:
            while True:
                conn = old_pool.get(block=False)
                if conn:
                    conn.close()
        except queue.Empty:
            pass
