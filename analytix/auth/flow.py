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

__all__ = ("run_flow",)

import logging
import re
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from pathlib import Path
from typing import Dict
from typing import Union
from urllib.parse import parse_qsl

from analytix.errors import AuthorisationError

REDIRECT_URI_PATTERN = re.compile("[^//]*//([^:]*):?([0-9]*)")

_log = logging.getLogger(__name__)


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
