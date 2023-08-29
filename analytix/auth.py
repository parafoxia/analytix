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

__all__ = (
    "Scopes",
    "Secrets",
    "Tokens",
    "state_token",
    "auth_uri",
    "token_uri",
    "refresh_uri",
    "run_flow",
)

import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass
from enum import Enum
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, List, Literal, Union
from urllib.parse import parse_qsl, urlencode

from analytix.errors import AuthorisationError
from analytix.types import PathLike, UriParams

OAUTH_CHECK_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo?access_token="
REDIRECT_URI_PATTERN = re.compile("[^//]*//([^:]*):?([0-9]*)")

_log = logging.getLogger(__name__)


class Scopes(Enum):
    """An enum for API scopes."""

    READONLY = "https://www.googleapis.com/auth/yt-analytics.readonly"
    """Omit revenue data from reports."""

    MONETARY_READONLY = "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"
    """Only include revenue data in reports."""

    ALL = f"{READONLY} {MONETARY_READONLY}"
    """Include all data in reports.

    !!! warning
        This is the default, though your channel needs to be partnered
        to use it. If your channel is not partnered, configure your
        client to use the `READONLY` scope.
    """


@dataclass(frozen=True)
class Secrets:
    """A dataclass representation of a secrets file.

    This should always be created using the `load_from` classmethod.

    Parameters
    ----------
    type : "installed" or "web"
        The application type. This will always be either "installed" or
        "web".
    client_id : str
        The client ID.
    project_id : str
        The name of the project.
    auth_uri : str
        The authorisation server endpoint URI.
    token_uri : str
        The token server endpoint URI.
    auth_provider_x509_cert_url : str
        The URL of the public x509 certificate, used to verify the
        signature on JWTs, such as ID tokens, signed by the
        authentication provider.
    client_secret : str
        The client secret.
    redirect_uris : list of str
        A list of valid redirection endpoint URIs. This list should
        match the list entered for the client ID on the API Access pane
        of the Google APIs Console.

    !!! warning
        If you're using an "installed" secrets file generated before 28
        Feb 2022, you will have an additional redirect URI for OOB
        authorisation. analytix no longer supports this authorisation
        method, but is backwards compatible with these older files.

        As a consequence of this, analytix will always use the **last**
        redirect URI in the list. If your secrets file contains multiple
        URIs, make sure the one you want to use is the last item in the
        list.
    """

    __slots__ = (
        "type",
        "client_id",
        "project_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_secret",
        "redirect_uris",
    )

    type: Literal["installed", "web"]
    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str
    redirect_uris: List[str]

    @classmethod
    def load_from(cls, path: PathLike) -> "Secrets":
        """Load secrets from a JSON file.

        Parameters
        ----------
        path : PathLike
            The path to your secrets file.

        Returns
        -------
        Secrets
            Your secrets.

        Raises
        ------
        FileNotFoundError
            No secrets file exists at the given path.
        JSONDecodeError
            The given file is not a valid JSON file.

        !!! example "Typical usage"
            ```py
            >>> Secrets.load_from("secrets.json")
            Secrets(type="installed", ...)
            ```
        """
        secrets_file = Path(path)

        if _log.isEnabledFor(logging.DEBUG):
            _log.debug("Loading secrets from %s", secrets_file.resolve())

        data = json.loads(secrets_file.read_text())
        key = next(iter(data.keys()))
        return cls(
            type=key,
            client_id=data[key]["client_id"],
            project_id=data[key]["project_id"],
            auth_uri=data[key]["auth_uri"],
            token_uri=data[key]["token_uri"],
            auth_provider_x509_cert_url=data[key]["auth_provider_x509_cert_url"],
            client_secret=data[key]["client_secret"],
            redirect_uris=data[key]["redirect_uris"],
        )


@dataclass()
class Tokens:
    """A dataclass representation of OAuth tokens.

    This should always be created using one of the available
    classmethods.

    Parameters
    ----------
    access_token : str
        A token that can be sent to a Google API.
    expires_in : int
        The remaining lifetime of the access token in seconds.
    scope : str
        The scopes of access granted by the access_token expressed as a
        list of space-delimited, case-sensitive strings.
    token_type : Bearer
        Identifies the type of token returned. This will always be
        "Bearer".
    refresh_token : str
        A token that can be used to refresh your access token.

    !!! warning
        The `expires_in` field is never updated by analytix, and as such
        will always be `3599` unless you update it yourself.
    """

    __slots__ = ("access_token", "expires_in", "scope", "token_type", "refresh_token")

    access_token: str
    expires_in: int
    scope: str
    token_type: Literal["Bearer"]
    refresh_token: str

    @classmethod
    def load_from(cls, path: PathLike) -> "Tokens":
        """Load tokens from a JSON file.

        Parameters
        ----------
        path : PathLike
            The path to your tokens file.

        Returns
        -------
        Tokens
            Your tokens.

        Raises
        ------
        FileNotFoundError
            No tokens file exists at the given path.
        JSONDecodeError
            The given file is not a valid JSON file.

        !!! example "Typical usage"
            ```py
            >>> Tokens.load_from("tokens.json")
            Tokens(access_token="1234567890", ...)
            ```
        """
        tokens_file = Path(path)

        if _log.isEnabledFor(logging.DEBUG):
            _log.debug("Loading tokens from %s", tokens_file.resolve())

        return cls.from_json(tokens_file.read_text())

    @classmethod
    def from_json(cls, data: Union[str, bytes]) -> "Tokens":
        """Load tokens from raw JSON data.

        Parameters
        ----------
        data : str or bytes
            Your tokens in JSON form.

        Returns
        -------
        Tokens
            Your tokens.

        Raises
        ------
        JSONDecodeError
            The given file is not a valid JSON file.

        !!! example "Typical usage"
            ```py
            >>> Tokens.from_json('{"access_token": "1234567890", ...}')
            Tokens(access_token="1234567890", ...)
            ```
        """
        return cls(**json.loads(data))

    def save_to(self, path: PathLike) -> None:
        """Save your tokens to disk.

        Parameters
        ----------
        path : PathLike
            The path to save your tokens to.

        Returns
        -------
        None
            This method doesn't return anything.

        !!! example "Typical usage"
            ```py
            Tokens.save_to("tokens.json")
            ```
        """
        tokens_file = Path(path)

        if _log.isEnabledFor(logging.DEBUG):
            _log.debug("Saving tokens to %s", tokens_file.resolve())

        attrs = {
            "access_token": self.access_token,
            "expires_in": self.expires_in,
            "scope": self.scope,
            "token_type": self.token_type,
            "refresh_token": self.refresh_token,
        }
        tokens_file.write_text(json.dumps(attrs))

    def refresh(self, data: Union[str, bytes]) -> "Tokens":
        """Updates your tokens to match those you refreshed.

        Parameters
        ----------
        data : str or bytes
            Your refreshed tokens in JSON form. These will not entirely
            replace your previous tokens, but instead update any
            out-of-date keys.

        Returns
        -------
        Tokens
            Your refreshed tokens.

        !!! info "See also"
            This method does not actually refresh your access token;
            for that, you'll need to use `Client.refresh_access_token`.

        !!! info "See also"
            To save tokens, you'll need the `save_to` method.

        !!! example "Typical usage"
            ```py
            >>> Tokens.refresh('{"access_token": "abcdefghij", ...}')
            Tokens(access_token="abcdefghij", ...)
            ```
        """
        attrs = json.loads(data)
        for key, value in attrs.items():
            setattr(self, key, value)
        return self


def state_token() -> str:
    """Generates a state token.

    Returns
    -------
    str
        A new state token.
    """
    return hashlib.sha256(os.urandom(1024)).hexdigest()


def auth_uri(secrets: Secrets, scopes: Scopes, port: int) -> UriParams:
    """Returns the authentication URI and parameters.

    Parameters
    ----------
    secrets : Secrets
        Your secrets.
    scopes : Scopes
        The scopes to allow in requests.
    port : int
        The websocket port you wish to use.

    Returns
    -------
    auth_uri : str
        The computed authentication URI.
    params : Dict[str, str]
        The query parameters as a dictionary.
    headers : Dict[str, str]
        Necessary request headers. This is always empty.
    """
    params = {
        "client_id": secrets.client_id,
        "nonce": state_token(),
        "response_type": "code",
        "redirect_uri": secrets.redirect_uris[-1] + (f":{port}" if port != 80 else ""),
        "scope": scopes.value,
        "state": state_token(),
        "access_type": "offline",
    }
    return f"{secrets.auth_uri}?{urlencode(params)}", params, {}


def token_uri(secrets: Secrets, code: str, redirect_uri: str) -> UriParams:
    """Returns the authentication URI and parameters.

    This returns the URI, data, and headers required to obtain your
    tokens.

    Parameters
    ----------
    secrets : Secrets
        Your secrets.
    code : str
        Your authentication code.
    redirect_uri : str
        Your redirect URI. This should be identical to the one you
        generated in `auth_uri`.

    Returns
    -------
    token_uri : str
        Your token URI.
    data : Dict[str, str]
        Necessary request data.
    headers : Dict[str, str]
        Necessary request headers.
    """
    data = {
        "code": code,
        "client_id": secrets.client_id,
        "client_secret": secrets.client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return secrets.token_uri, data, headers


def refresh_uri(secrets: Secrets, token: str) -> UriParams:
    """Returns the authentication URI and parameters.

    This returns the URI, data, and headers required to refresh your
    tokens.

    Parameters
    ----------
    secrets : Secrets
        Your secrets.
    token : str
        Your refresh token.

    Returns
    -------
    token_uri : str
        Your token URI.
    data : Dict[str, str]
        Necessary request data.
    headers : Dict[str, str]
        Necessary request headers.
    """
    data = {
        "client_id": secrets.client_id,
        "client_secret": secrets.client_secret,
        "refresh_token": token,
        "grant_type": "refresh_token",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return secrets.token_uri, data, headers


def run_flow(auth_params: Dict[str, str]) -> str:
    """Start a webserver and listen for an authentication code.

    You should not use this if you are building a web application.

    Parameters
    ----------
    auth_params : Dict[str, str]
        The parameters generated from the `auth_uri` method.

    Returns
    -------
    str
        Your authentication code.

    Raises
    ------
    AuthorisationError
        * You provided an invalid redirect URI
        * The received state does not match the generated one
    """
    if not (match := REDIRECT_URI_PATTERN.match(auth_params["redirect_uri"])):
        raise AuthorisationError("invalid redirect URI")

    class RequestHandler(BaseHTTPRequestHandler):
        def log_request(
            self, code: Union[int, str] = "-", _: Union[int, str] = "-"
        ) -> None:
            _log.debug(f"Received request ({code})")

        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.server: "Server"
            self.server.query_params = dict(parse_qsl(self.path.split("?")[1]))
            self.wfile.write((Path(__file__).parent / "landing.html").read_bytes())

    class Server(HTTPServer):
        def __init__(self, address: str, port: int) -> None:
            super().__init__((address, port), RequestHandler)
            self.query_params: Dict[str, str] = {}
            _log.debug("Started webserver on %s:%d", self.server_name, self.server_port)

        def server_close(self) -> None:
            super().server_close()
            _log.debug("Closed webserver")

    host, port = match.groups()
    ws = Server(host, int(port or 80))

    try:
        ws.handle_request()
    except KeyboardInterrupt as exc:
        raise exc
    finally:
        ws.server_close()

    if auth_params["state"] != ws.query_params["state"]:
        raise AuthorisationError("invalid state")

    return ws.query_params["code"]
