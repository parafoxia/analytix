# Copyright (c) 2021-present, Ethan Henderson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__all__ = ("Secrets",)

import json
import logging
import re
import secrets
import webbrowser
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from io import StringIO
from io import TextIOBase
from os import PathLike
from pathlib import Path
from typing import Literal
from urllib.parse import parse_qs
from urllib.parse import urlencode

from analytix.auth.scopes import Scopes
from analytix.auth.tokens import Tokens
from analytix.errors import AuthorisationError
from analytix.mixins import RequestMixin

REDIRECT_URI_PATTERN = re.compile("[^//]*//([^:]*):?([0-9]*)")

_log = logging.getLogger(__name__)


class _RequestHandler(BaseHTTPRequestHandler):
    def log_request(
        self,
        code: int | str = "-",
        _: int | str = "-",
    ) -> None:
        _log.debug(f"Received request ({code})")

    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        self.server: _Server
        self.server.query_params = dict(parse_qs(self.path.split("?")[1]))
        self.wfile.write((Path(__file__).parent / "landing.html").read_bytes())


class _Server(HTTPServer):
    def __init__(self, address: str, port: int) -> None:
        super().__init__((address, port), _RequestHandler)
        self.query_params: dict[str, str] = {}
        _log.debug("Started webserver on %s:%d", self.server_name, self.server_port)
        _log.debug("Waiting for user to provide access...")

    def server_close(self) -> None:
        super().server_close()
        _log.debug("Closed webserver")


@dataclass(frozen=True)
class ClientSecrets:
    """A set of client secrets.

    Attributes
    ----------
    client_id
        The client ID.
    client_secret
        The client secret.
    redirect_uris
        A list of valid redirection endpoint URIs. This list should
        match the list entered for the client ID on the API Access pane
        of the Google APIs Console.
    auth_uri
        The authorisation server endpoint URI.
    token_uri
        The token server endpoint URI.
    client_email
        The service account email associated with the client.
    auth_provider_x509_cert_url
        The URL of the public x509 certificate, used to verify the
        signature on JWTs, such as ID tokens, signed by the
        authentication provider.
    client_x509_cert_url
        The URL of the public x509 certificate, used to verify JWTs
        signed by the client.

    Notes
    -----
    It is recommended that you use the `Secrets` class instead of this
    directly.
    """

    client_id: str
    client_secret: str
    redirect_uris: list[str]
    auth_uri: str
    token_uri: str
    client_email: str | None = None
    auth_provider_x509_cert_url: str | None = None
    client_x509_cert_url: str | None = None


@dataclass(frozen=True)
class AuthContext(RequestMixin):
    """An authorisation context.

    Attributes
    ----------
    client_id
        The client ID.
    client_secret
        The client secret.
    redirect_uri
        The redirect UR to use in the request.
    auth_uri
        The authorisation server endpoint URI.
    token_uri
        The token server endpoint URI.
    state
        The state token.
    """

    client_id: str
    client_secret: str
    redirect_uri: str
    auth_uri: str
    token_uri: str
    state: str

    def open_browser(self) -> bool:
        """Open a web browser to the authorisation page.

        Returns
        -------
        bool
            Whether the browser was opened successfully.
        """
        _log.debug("Opening web browser")
        success = webbrowser.open(self.auth_uri, 0, autoraise=True)
        if not success:
            _log.warning("Failed to open web browser")
        return success

    def fetch_code(self) -> str:
        """Fetch the authorisation code.

        Returns
        -------
        str
            The authorisation code.

        Raises
        ------
        AuthorisationError
            * The provided redirect URI is invalid
            * The received state does not match the generated one
        """
        _log.debug("Fetching authorisation code")

        if not (match := REDIRECT_URI_PATTERN.match(self.redirect_uri)):
            raise AuthorisationError("invalid redirect URI")

        host, port = match.groups()
        ws = _Server(host, int(port or 80))

        try:
            ws.handle_request()
        finally:
            ws.server_close()

        if self.state != ws.query_params["state"][0]:
            raise AuthorisationError("invalid state")

        code = ws.query_params["code"][0]

        if _log.isEnabledFor(logging.DEBUG):
            hidden_code = f"{code[:4]}...{code[-4:]}"
            _log.debug("Received code: %s", hidden_code)

        return code

    def fetch_tokens(self, code: str | None = None) -> Tokens:
        """Fetch the authorisation tokens.

        Parameters
        ----------
        code : str, optional
            The authorisation code. If this is not provided, one will be
            fetched.

        Returns
        -------
        Tokens
            Your tokens.

        Raises
        ------
        AuthorisationError
            There was a problem fetching the tokens. See the error
            message for more information.
        """
        if code is None:
            code = self.fetch_code()

        _log.debug("Fetching access token")

        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        with self._request(self.token_uri, data=data, headers=headers) as resp:
            if resp.status > 399:
                error = json.loads(resp.data)
                raise AuthorisationError(
                    f"could not authorise: {error['error_description']} "
                    f"({error['error']})",
                )

            return Tokens.read_json(StringIO(resp.data.decode("utf-8")))


@dataclass(frozen=True)
class Secrets:
    """A secrets manager.

    Attributes
    ----------
    type
        The client ID type. This will be either "installed" or "web".
    resource
        The client secrets resource.
    scopes
        The scopes to allow in requests.
    """

    __slots__ = ("resource", "scopes", "type")

    type: Literal["installed", "web"]
    resource: ClientSecrets
    scopes: Scopes

    @classmethod
    def read_json(
        cls,
        path_or_buf: str | PathLike[str] | TextIOBase,
        scopes: Scopes,
    ) -> "Secrets":
        """Convert a JSON string into a set of secrets.

        !!! note "New in version 6.0"

        Parameters
        ----------
        path_or_buf
            The path to your secrets file or a file-like object to
            read from.
        scopes : Scopes
            The scopes to allow in requests.

        Returns
        -------
        Secrets
            Your secrets.

        Examples
        --------
        >>> with open("secrets.json", "r") as f:
        ...     secrets = Secrets.read_json(f)
        >>> secrets
        Secrets(type="installed", ...)

        Loading from a file.

        >>> Secrets.read_json("secrets.json")
        Secrets(type="installed", ...)

        Providing custom scopes.

        >>> Secrets.read_json("secrets.json", scopes=Scopes.ALL_READONLY)
        Secrets(type="installed", resource=..., scopes=Scopes.ALL_READONLY)
        """
        if isinstance(path_or_buf, (str, PathLike)):
            data = Path(path_or_buf).read_text()
        elif isinstance(path_or_buf, TextIOBase):
            data = path_or_buf.read()
        else:
            raise TypeError(
                "Expected str, PathLike, or TextIOBase, "
                f"got {type(path_or_buf).__name__}",
            )

        data = json.loads(data)
        typ = next(iter(data.keys()))
        params = data[typ]
        return cls(
            type=typ,
            resource=ClientSecrets(
                client_id=params["client_id"],
                client_secret=params["client_secret"],
                redirect_uris=params["redirect_uris"],
                auth_uri=params["auth_uri"],
                token_uri=params["token_uri"],
                client_email=params.get("client_email"),
                auth_provider_x509_cert_url=params.get("auth_provider_x509_cert_url"),
                client_x509_cert_url=params.get("client_x509_cert_url"),
            ),
            scopes=scopes,
        )

    @contextmanager
    def auth_context(self, *, ws_port: int | None = None) -> Iterator[AuthContext]:
        """Create an authorisation context.

        This method is a context manager.

        Parameters
        ----------
        ws_port : int, optional
            The port the client's webserver will use during
            authorisation. If this is not provided, a sensible default
            will be used (normally `80` or `8080`).

        Yields
        ------
        AuthContext
            The authorisation context.

        Examples
        --------
        >>> with secrets.auth_context() as ctx:
        ...     tokens = ctx.fetch_tokens()
        """
        redirect_uri = next(
            uri
            for uri in self.resource.redirect_uris
            if uri != "oob" and "urn:ietf:wg:oauth:2.0:oob" not in uri
        )

        if not ws_port and self.type == "installed":
            ws_port = 8080
        if ws_port:
            redirect_uri = f"{redirect_uri.rstrip('/')}:{ws_port}"
        _log.debug("Using redirect URI: %s", redirect_uri)

        auth_params = {
            "client_id": self.resource.client_id,
            "nonce": secrets.token_urlsafe(),
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": self.scopes.formatted,
            "state": (state := secrets.token_urlsafe()),
            "access_type": "offline",
        }
        yield AuthContext(
            client_id=self.resource.client_id,
            client_secret=self.resource.client_secret,
            redirect_uri=redirect_uri,
            auth_uri=f"{self.resource.auth_uri}?{urlencode(auth_params)}",
            token_uri=self.resource.token_uri,
            state=state,
        )
