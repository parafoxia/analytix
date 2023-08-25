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
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, List, Mapping, Union
from urllib.parse import parse_qsl, urlencode

from analytix.errors import AuthorisationError
from analytix.experimental.types import PathLike, UriParams
from analytix.oidc import Scopes

OAUTH_CHECK_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo?access_token="
REDIRECT_URI_PATTERN = re.compile("[^//]*//([^:]*):?([0-9]*)")

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Secrets:
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
    redirect_uris: List[str]

    @classmethod
    def load_from(cls, path: PathLike) -> "Secrets":
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
    __slots__ = ("access_token", "expires_in", "scope", "token_type", "refresh_token")

    access_token: str
    expires_in: int
    scope: str
    token_type: str
    refresh_token: str

    @classmethod
    def from_json(cls, data: Union[str, bytes]) -> "Tokens":
        return cls(**json.loads(data))

    @classmethod
    def load_from(cls, path: PathLike) -> "Tokens":
        tokens_file = Path(path)

        if _log.isEnabledFor(logging.DEBUG):
            _log.debug("Loading tokens from %s", tokens_file.resolve())

        return cls.from_json(tokens_file.read_text())

    def save_to(self, path: PathLike) -> None:
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
        attrs = json.loads(data)
        for key, value in attrs.items():
            setattr(self, key, value)
        return self


def state_token() -> str:
    return hashlib.sha256(os.urandom(1024)).hexdigest()


def auth_uri(secrets: Secrets, scopes: Scopes, port: int) -> UriParams:
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
    data = {
        "client_id": secrets.client_id,
        "client_secret": secrets.client_secret,
        "refresh_token": token,
        "grant_type": "refresh_token",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return secrets.token_uri, data, headers


def run_flow(auth_params: Mapping[str, str]) -> str:
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
