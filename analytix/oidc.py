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

"""OpenID Connect functionality for client authorisation.

These are mainly documentated to provide a reference rather than to aid
in their use, as everything is called automatically when needed. You may
find use in some of the helper functions if you are building a web
application.

!!! info "See also"
    This follows the OpenID Connect specification as described in the
    [Google Identity documentation](https://developers.google.com/
    identity/openid-connect/openid-connect).
"""

from __future__ import annotations

__all__ = (
    "Secrets",
    "Tokens",
    "state_token",
    "auth_uri",
    "token_uri",
    "refresh_uri",
    "authenticate",
)

import hashlib
import json
import logging
import os
import re
import typing as t
from dataclasses import dataclass
from http import server
from pathlib import Path
from urllib.parse import parse_qsl, urlencode

import aiofiles

import analytix
from analytix.errors import AuthorisationError
from analytix.types import SecretT, TokenT

if t.TYPE_CHECKING:
    from analytix.types import AuthUriT, TokenUriT

REDIRECT_URI_PATTERN = re.compile("[^//]*//([^:]*):?([0-9]*)")

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Secrets:
    """A representation of your client secrets.

    This should always be created using the `from_file` classmethod.

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

    type: str
    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str
    redirect_uris: list[str]

    def __str__(self) -> str:
        return self.project_id

    def __getitem__(self, key: str) -> SecretT:
        return t.cast(SecretT, getattr(self, key))

    @classmethod
    def from_file(cls, path: Path | str) -> Secrets:
        """Load secrets from a JSON file.

        Parameters
        ----------
        path : Path object or str
            The filepath to the secrets file.

        Returns
        -------
        Secrets
            The newly created instance.

        Raises
        ------
        FileNotFoundError
            No secrets file exists at the given path.
        JSONDecodeError
            The given file is not a valid JSON file.
        """

        if not isinstance(path, Path):
            path = Path(path)

        _log.debug(f"Loading secrets from {path.resolve()}")

        with open(path) as f:
            data = json.loads(f.read())

        key = next(iter(data.keys()))
        _log.info(f"Secrets loaded (type: {key})!")
        return cls(type=key, **data[key])

    def to_dict(self) -> dict[str, dict[str, SecretT]]:
        """Returns the secrets as a dictionary.

        Returns
        -------
        Mapping of str-SecretT
            The dictionary of secrets. All values are strings except
            `redirect_uris` which is a list of strings.
        """

        return {
            self.type: {
                "client_id": self.client_id,
                "project_id": self.project_id,
                "auth_uri": self.auth_uri,
                "token_uri": self.token_uri,
                "auth_provider_x509_cert_url": self.auth_provider_x509_cert_url,
                "client_secret": self.client_secret,
                "redirect_uris": self.redirect_uris,
            },
        }


@dataclass()
class Tokens:
    """A representation of your tokens.

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
    token_type: str
    refresh_token: str

    def __getitem__(self, key: str) -> TokenT:
        return t.cast(TokenT, getattr(self, key))

    @classmethod
    def from_dict(cls, data: dict[str, TokenT]) -> Tokens:
        """Load tokens from a dictionary.

        Parameters
        ----------
        data : dict of str-TokenT
            The token data. Usually the response data from the Google
            OAuth API.

        Returns
        -------
        Tokens
            The newly created instance.
        """

        return cls(**data)  # type: ignore

    @classmethod
    async def from_file(cls, path: Path | str) -> Tokens:
        """Load tokens from a JSON file.

        Parameters
        ----------
        path : Path object or str
            The filepath to the tokens file.

        Returns
        -------
        Tokens
            The newly created instance.

        Raises
        ------
        FileNotFoundError
            No tokens file exists at the given path.
        JSONDecodeError
            The given file is not a valid JSON file.
        """

        if not isinstance(path, Path):
            path = Path(path)

        _log.debug(f"Loading tokens from {path.resolve()}")

        async with aiofiles.open(path) as f:
            data = json.loads(await f.read())

        _log.info("Tokens loaded!")
        return cls(**data)

    def to_dict(self) -> dict[str, TokenT]:
        """Returns the tokens as a dictionary.

        Returns
        -------
        Mapping of str-TokenT
            The dictionary of tokens. All values are strings except
            `expires_in` which is an integer.
        """

        return {
            "access_token": self.access_token,
            "expires_in": self.expires_in,
            "scope": self.scope,
            "token_type": self.token_type,
            "refresh_token": self.refresh_token,
        }

    def update(self, data: dict[str, TokenT]) -> None:
        """Updates the tokens in place.

        Parameters
        ----------
        data : JSON object
            The data to update. Usually the new tokens after refreshing.

        Returns
        -------
        None

        !!! info "See also"
            To write tokens, view the `write()` method.
        """

        for k, v in data.items():
            setattr(self, k, v)

        _log.info("Tokens updated!")

    async def write(self, path: Path | str) -> None:
        """Writes the tokens to disk.

        Parameters
        ----------
        path : Path object or str
            The filepath to save the tokens to.

        Returns
        -------
        None
        """

        if not isinstance(path, Path):
            path = Path(path)

        async with aiofiles.open(path, "w") as f:
            await f.write(json.dumps(self.to_dict()))

        _log.info(f"Tokens saved to {path.resolve()}")


def state_token() -> str:
    """Generates a state token.

    Returns
    -------
    str
        A new state token.
    """

    return hashlib.sha256(os.urandom(1024)).hexdigest()


def auth_uri(secrets: Secrets, port: int) -> AuthUriT:
    """Returns the authentication URI and parameters.

    Parameters
    ----------
    secrets : Secrets
        Your client secrets.
    port : int
        The webserver port you wish to use.

    Returns
    -------
    auth_uri : str
        The computed authentication URI.
    params : Mapping of str-str
        A dictionary representation of the query string.
    """

    params = {
        "client_id": secrets.client_id,
        "nonce": state_token(),
        "response_type": "code",
        "redirect_uri": secrets.redirect_uris[-1] + (f":{port}" if port != 80 else ""),
        "scope": " ".join(analytix.API_SCOPES),
        "state": state_token(),
        "access_type": "offline",
    }
    return f"{secrets.auth_uri}?{urlencode(params)}", params


def token_uri(secrets: Secrets, code: str, auth_params: dict[str, str]) -> TokenUriT:
    """Returns the token URI, data, and headers.

    Parameters
    ----------
    secrets : Secrets
        Your client secrets.
    code : str
        Your authentication code.
    auth_params : Mapping of str-str
        The parameters generated from the `auth_uri()` method.

    Returns
    -------
    token_uri : str
        The computed token URI.
    data : Mapping of str-str
        The request data.
    headers : Mapping of str-str
        The request header.
    """

    data = {
        "code": code,
        "client_id": secrets.client_id,
        "client_secret": secrets.client_secret,
        "redirect_uri": auth_params["redirect_uri"],
        "grant_type": "authorization_code",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return secrets.token_uri, data, headers


def refresh_uri(secrets: Secrets, token: str) -> TokenUriT:
    """Returns the refresh URI, data, and headers.

    Parameters
    ----------
    secrets : Secrets
        Your client secrets.
    token : str
        Your refresh token.

    Returns
    -------
    token_uri : str
        The computed refresh URI.
    data : Mapping of str-str
        The request data.
    headers : Mapping of str-str
        The request header.
    """

    data = {
        "client_id": secrets.client_id,
        "client_secret": secrets.client_secret,
        "refresh_token": token,
        "grant_type": "refresh_token",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return secrets.token_uri, data, headers


class _RequestHandler(server.BaseHTTPRequestHandler):
    def log_request(self, code: int | str = "-", _: int | str = "-") -> None:
        _log.debug(f"Received request ({code})")

    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.server: _Server  # Overwrite type so code is exposed.
        self.server.query = dict(parse_qsl(self.path.split("?")[1]))
        self.wfile.write((Path(__file__).parent / "landing.html").read_bytes())


class _Server(server.HTTPServer):
    def __init__(self, address: str, port: int) -> None:
        super().__init__((address, port), _RequestHandler)
        self.query: dict[str, str] = {}
        _log.info(f"Started webserver on {self.server_name}:{self.server_port}")

    def server_close(self) -> None:
        super().server_close()
        _log.info("Closed webserver")


def authenticate(auth_params: dict[str, str]) -> str:
    """Start a webserver and listen for an authentication code.

    Parameters
    ----------
    auth_params : Mapping of str-str
        The parameters generated from the `auth_uri()` method.

    Returns
    -------
    str
        The authentication code.

    Raises
    ------
    AuthorisationError
        * You provided an invalid redirect URI
        * The received state does not match the generated one
    """

    match = REDIRECT_URI_PATTERN.match(auth_params["redirect_uri"])
    if not match:
        raise AuthorisationError("invalid redirect URI")

    host, port = match.groups()
    ws = _Server(host, int(port or 80))

    try:
        ws.handle_request()
    except KeyboardInterrupt as exc:
        raise exc
    finally:
        ws.server_close()

    if auth_params["state"] != ws.query["state"]:
        raise AuthorisationError("invalid state")

    return ws.query["code"]
