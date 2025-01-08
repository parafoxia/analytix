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

"""Helper methods for client authorisation.

You will only need to use these if you're planning to subclass the base
client.

???+ info "See also"
    This follows the OpenID Connect specification as described in the
    [Google Identity documentation](https://developers.google.com/
    identity/openid-connect/openid-connect).
"""

__all__ = (
    "Scopes",
    "Secrets",
    "Tokens",
    "auth_uri",
    "refresh_uri",
    "run_flow",
    "state_token",
    "token_uri",
)

import json
import logging
import re
import secrets
import sys
from dataclasses import dataclass
from enum import Flag
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from pathlib import Path
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union
from urllib.parse import parse_qsl
from urllib.parse import urlencode

from analytix.errors import AuthorisationError
from analytix.types import PathLike
from analytix.types import UriParams

REDIRECT_URI_PATTERN = re.compile("[^//]*//([^:]*):?([0-9]*)")
SCOPE_URLS = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]

_log = logging.getLogger(__name__)


class Scopes(Flag):
    """An enum for API scopes.

    Possible values are:

    * `READONLY` — Don't include revenue data from reports
    * `MONETARY_READONLY` — Only include revenue data from reports
    * `ALL` — Include all data in reports (this does not enable JWT
      scopes)
    * `OPENID` — Enable the OpenID scope
    * `PROFILE` — Include profile information in JWTs
    * `EMAIL` — Include email information in JWTs
    * `ALL_JWT` — Include all available information in JWTs

    ???+ note "Changed in version 5.1"
        * Added the `OPENID`, `PROFILE`, `EMAIL`, and `ALL_JWT` scopes
        * This now works like a flag enum rather than a normal one; this
          doesn't introduce any breaking changes (unless you're using
          analytix in a particularly unconventional way), but does mean
          you can now use a `|` to concatenate scopes
    """

    READONLY = 1 << 0
    MONETARY_READONLY = 1 << 1
    ALL = READONLY | MONETARY_READONLY
    OPENID = 1 << 2
    PROFILE = 1 << 3
    EMAIL = 1 << 4
    ALL_JWT = OPENID | PROFILE | EMAIL

    @property
    def formatted(self) -> str:
        return " ".join(
            url for i, url in enumerate(SCOPE_URLS) if self.value & (1 << i)
        )

    def validate(self) -> None:
        if not (self.value & (1 << 0) or self.value & (1 << 1)):
            raise AuthorisationError(
                "the READONLY or MONETARY_READONLY scope must be provided",
            )


@dataclass(frozen=True)
class Secrets:
    """A set of API secrets.

    This should always be created using the `load_from` classmethod.

    Parameters
    ----------
    type
        The application type. This will always be either "installed" or
        "web".
    client_id
        The client ID.
    project_id
        The name of the project.
    auth_uri
        The authorisation server endpoint URI.
    token_uri
        The token server endpoint URI.
    auth_provider_x509_cert_url
        The URL of the public x509 certificate, used to verify the
        signature on JWTs, such as ID tokens, signed by the
        authentication provider.
    client_secret
        The client secret.
    redirect_uris
        A list of valid redirection endpoint URIs. This list should
        match the list entered for the client ID on the API Access pane
        of the Google APIs Console.
    """

    __slots__ = (
        "auth_provider_x509_cert_url",
        "auth_uri",
        "client_id",
        "client_secret",
        "project_id",
        "redirect_uris",
        "token_uri",
        "type",
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

        ???+ note "Changed in version 5.0"
            This used to be `from_file`.

        Parameters
        ----------
        path
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

        Examples
        --------
        >>> Secrets.load_from("secrets.json")
        Secrets(type="installed", ...)
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


@dataclass(**({"slots": True} if sys.version_info >= (3, 10) else {}))
class Tokens:
    """OAuth tokens.

    This should always be created using one of the available
    classmethods.

    Parameters
    ----------
    access_token
        A token that can be sent to a Google API.
    expires_in
        The remaining lifetime of the access token in seconds.
    scope
        The scopes of access granted by the access_token expressed as a
        list of space-delimited, case-sensitive strings.
    token_type
        Identifies the type of token returned. This will always be
        "Bearer".
    refresh_token
        A token that can be used to refresh your access token.
    id_token
        A JWT that contains identity information about the user that is
        digitally signed by Google. This will be `None` if you did not
        specifically request JWT tokens when authorising.

    Warnings
    --------
    The `expires_in` field is never updated by analytix, and as such
    will always be `3599` unless you update it yourself.
    """

    access_token: str
    expires_in: int
    scope: str
    token_type: Literal["Bearer"]
    refresh_token: str
    id_token: Optional[str] = None

    @classmethod
    def load_from(cls, path: PathLike) -> "Tokens":
        """Load tokens from a JSON file.

        ???+ note "Changed in version 5.0"
            This used to be `from_file`.

        Parameters
        ----------
        path
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

        Examples
        --------
        >>> Tokens.load_from("tokens.json")
        Tokens(access_token="1234567890", ...)
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
        data
            Your tokens in JSON form.

        Returns
        -------
        Tokens
            Your tokens.

        Raises
        ------
        JSONDecodeError
            The given file is not a valid JSON file.

        Examples
        --------
        >>> Tokens.from_json('{"access_token": "1234567890", ...}')
        Tokens(access_token="1234567890", ...)
        """
        return cls(**json.loads(data))

    def save_to(self, path: PathLike) -> None:
        """Save your tokens to disk.

        ???+ note "Changed in version 5.0"
            This used to be `write`.

        Parameters
        ----------
        path
            The path to save your tokens to.

        Returns
        -------
        None
            This method doesn't return anything.

        Examples
        --------
        >>> Tokens.save_to("tokens.json")
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
            **({"id_token": self.id_token} if self.id_token else {}),
        }
        tokens_file.write_text(json.dumps(attrs))

    def refresh(self, data: Union[str, bytes]) -> "Tokens":
        """Updates your tokens to match those you refreshed.

        ???+ note "Changed in version 5.0"
            This used to be `update`.

        Parameters
        ----------
        data
            Your refreshed tokens in JSON form. These will not entirely
            replace your previous tokens, but instead update any
            out-of-date keys.

        Returns
        -------
        Tokens
            Your refreshed tokens.

        See Also
        --------
        * This method does not actually refresh your access token;
          for that, you'll need to use `Client.refresh_access_token`.
        * To save tokens, you'll need the `save_to` method.

        Examples
        --------
        >>> Tokens.refresh('{"access_token": "abcdefghij", ...}')
        Tokens(access_token="abcdefghij", ...)
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

    Examples
    --------
    >>> state_token()
    '385cdc1c6e9410120755ecf1c0558299be58bd3bcc6f515addaa817df5e10fd2'
    """
    return secrets.token_hex()


def auth_uri(secrets: Secrets, scopes: Scopes, port: int) -> UriParams:
    """Returns the authentication URI and parameters.

    ???+ note "Changed in version 5.0"
        * This now takes scopes as a parameter
        * This now returns headers (albeit always empty) to be more
          consistent with other functions
        * The redirect URI to use is now chosen more intelligently --
          it will be the first in the list not intended to be used in
          OOB authorisation.

    Parameters
    ----------
    secrets
        Your secrets.
    scopes
        The scopes to allow in requests.
    port
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
    redirect_uri = next(
        uri
        for uri in secrets.redirect_uris
        if uri != "oob" and "urn:ietf:wg:oauth:2.0:oob" not in uri
    )

    params = {
        "client_id": secrets.client_id,
        "nonce": state_token(),
        "response_type": "code",
        "redirect_uri": redirect_uri + (f":{port}" if port != 80 else ""),
        "scope": scopes.formatted,
        "state": state_token(),
        "access_type": "offline",
    }

    return f"{secrets.auth_uri}?{urlencode(params)}", params, {}


def token_uri(secrets: Secrets, code: str, redirect_uri: str) -> UriParams:
    """Returns the token URI, data, and headers.

    Parameters
    ----------
    secrets
        Your secrets.
    code
        Your authentication code.
    redirect_uri
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
    """Returns the refresh URI, data, and headers.

    Parameters
    ----------
    secrets
        Your secrets.
    token
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

    ???+ note "Changed in version 5.0"
        This used to be `authenticate`.

    Parameters
    ----------
    auth_params
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
            self,
            code: Union[int, str] = "-",
            _: Union[int, str] = "-",
        ) -> None:
            _log.debug(f"Received request ({code})")

        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.server: Server
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
