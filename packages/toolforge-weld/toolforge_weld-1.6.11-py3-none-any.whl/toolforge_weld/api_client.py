from __future__ import annotations

import base64
import ssl
from typing import Any, Callable, Iterator, Optional, Union

import click
import OpenSSL
import requests
import requests.hooks
import urllib3
from urllib3 import Retry
from urllib3.contrib.pyopenssl import PyOpenSSLContext

from toolforge_weld.kubernetes_config import Kubeconfig, ToolforgeKubernetesConfigError
from toolforge_weld.utils import USER_AGENT


# TODO: these are available natively starting with python 3.9
# but toolforge bastions run python 3.7 as of this writing
def _removesuffix(input_string: str, suffix: str) -> str:
    if suffix and input_string.endswith(suffix):
        return input_string[: -len(suffix)]  # noqa: E203
    return input_string


def _removeprefix(input_string: str, prefix: str) -> str:
    if prefix and input_string.startswith(prefix):
        return input_string[len(prefix) :]  # noqa: E203
    return input_string


# Unfortunately, there's no support for loading certificates directly from memory instead of reading it from the filesystem
# This helps work around that (from https://stackoverflow.com/questions/45410508/python-requests-ca-certificates-as-a-string)
class ClientSideCertificateHTTPAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, *args, cert, key, **kwargs):
        self._cert = cert
        self._key = key
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        # This is the one that works for us, might change :/
        ctx = PyOpenSSLContext(ssl.PROTOCOL_SSLv23)
        kwargs["ssl_context"] = ctx
        ctx._ctx.use_certificate(self._cert)
        ctx._ctx.use_privatekey(self._key)
        return super().init_poolmanager(*args, **kwargs)


ConnectionError = Union[
    requests.exceptions.HTTPError, requests.exceptions.ConnectionError
]
"""A type alias for any error types that might be handled by a connection error handler."""


class ToolforgeClient:
    """Toolforge API client."""

    def __init__(
        self,
        *,
        server: str,
        kubeconfig: Kubeconfig,
        user_agent: str,
        # temporary bump T376710
        timeout: int = 20,
        exception_handler: Optional[
            Callable[[requests.exceptions.HTTPError], Exception]
        ] = None,
        connect_exception_handler: Optional[
            Callable[[ConnectionError], Exception]
        ] = None,
    ):
        self.exception_handler = exception_handler
        self.connect_exception_handler = connect_exception_handler

        self.timeout = timeout
        self.server = server
        self.session = requests.Session()

        if kubeconfig.client_cert_file and kubeconfig.client_key_file:
            self.session.cert = (
                str(kubeconfig.client_cert_file),
                str(kubeconfig.client_key_file),
            )
        elif kubeconfig.client_cert_data and kubeconfig.client_key_data:
            try:
                cert = OpenSSL.crypto.load_certificate(
                    OpenSSL.crypto.FILETYPE_PEM,
                    kubeconfig.client_cert_data.encode("utf-8"),
                )
            except OpenSSL.crypto.Error:
                # try base64 decoding
                cert = OpenSSL.crypto.load_certificate(
                    OpenSSL.crypto.FILETYPE_PEM,
                    base64.b64decode(kubeconfig.client_cert_data),
                )

            try:
                key = OpenSSL.crypto.load_privatekey(
                    OpenSSL.crypto.FILETYPE_PEM, kubeconfig.client_key_data
                )
            except OpenSSL.crypto.Error:
                # try base64 decoding
                key = OpenSSL.crypto.load_privatekey(
                    OpenSSL.crypto.FILETYPE_PEM,
                    base64.b64decode(kubeconfig.client_key_data),
                )

            adapter = ClientSideCertificateHTTPAdapter(
                cert=cert, key=key, max_retries=Retry(total=10, backoff_factor=0.5)
            )
            self.session.mount(_removesuffix(self.server, "/"), adapter)
        elif kubeconfig.token:
            self.session.headers["Authorization"] = f"Bearer {kubeconfig.token}"
        else:
            raise ToolforgeKubernetesConfigError(
                "Kubernetes configuration is missing authentication details"
            )

        if kubeconfig.ca_file:
            self.session.verify = str(kubeconfig.ca_file)
        else:
            self.session.verify = False

            # T253412: Disable warnings about unverifed TLS certs when talking to the
            # Kubernetes API endpoint
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.session.headers["User-Agent"] = f"{user_agent} {USER_AGENT}"

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        try:
            self.session.headers.update(kwargs.pop("headers", {}))
            response = self.session.request(method, **self.make_kwargs(url, **kwargs))
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError as e:
            if self.connect_exception_handler:
                raise self.connect_exception_handler(e) from e
            raise e
        except requests.exceptions.HTTPError as e:
            # Raise a connection error on proxy (= api-gateway) level
            # errors to provide more uniform error messages.
            if (
                e.response is not None
                and e.response.status_code in (502, 503)
                and self.connect_exception_handler
            ):
                raise self.connect_exception_handler(e) from e

            if self.exception_handler:
                exception_object = self.exception_handler(e)
                if hasattr(exception_object, "context"):
                    self._display_messages(exception_object.context)
                raise exception_object from e
            raise e

    def _display_messages(self, response: dict[str, Any]):
        # error_messages are not being handled here since those are handled in _make_request
        messages = response.get("messages", {})

        info_messages = messages.get("info", [])
        for message in info_messages:
            click.echo(click.style(message, fg="blue"))

        warning_messages = messages.get("warning", [])
        for message in warning_messages:
            click.echo(click.style(f"Warning: {message}", fg="yellow"), err=True)

    def make_kwargs(self, url: str, **kwargs) -> dict[str, Any]:
        """Setup kwargs for a Requests request."""
        kwargs["url"] = "{}/{}".format(
            _removesuffix(self.server, "/"), _removeprefix(url, "/")
        )

        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        return kwargs

    def get(self, url, display_messages: bool = True, **kwargs) -> dict[str, Any]:
        """GET request."""
        response = self._make_request("GET", url, **kwargs).json()
        display_messages and self._display_messages(response)
        return response

    def post(self, url, display_messages: bool = True, **kwargs) -> dict[str, Any]:
        """POST request."""
        response = self._make_request("POST", url, **kwargs).json()
        display_messages and self._display_messages(response)
        return response

    def put(self, url, display_messages: bool = True, **kwargs) -> dict[str, Any]:
        """PUT request."""
        response = self._make_request("PUT", url, **kwargs).json()
        display_messages and self._display_messages(response)
        return response

    def patch(self, url, display_messages: bool = True, **kwargs) -> dict[str, Any]:
        """PATCH request."""
        response = self._make_request("PATCH", url, **kwargs).json()
        display_messages and self._display_messages(response)
        return response

    def delete(self, url, display_messages: bool = True, **kwargs) -> dict[str, Any]:
        """DELETE request."""
        response = self._make_request("DELETE", url, **kwargs).json()
        display_messages and self._display_messages(response)
        return response

    def get_raw_lines(self, url, method: str = "GET", **kwargs) -> Iterator[str]:
        """Stream the raw lines from a specific API endpoint."""
        with self._make_request(
            method,
            url,
            headers={},
            stream=True,
            **kwargs,
        ) as r:
            yield from r.iter_lines(decode_unicode=True)
