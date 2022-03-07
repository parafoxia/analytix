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

from __future__ import annotations

import hashlib
import logging
import time
import typing as t

import analytix

if t.TYPE_CHECKING:
    from analytix.secrets import Secrets
    from analytix.types import DataHeadersT

log = logging.getLogger(__name__)


def create_state() -> str:
    """Create a random state for requests.

    Returns:
        The state as a 64-character long hexadecimal string.
    """

    return hashlib.sha256(f"{time.time()}".encode("utf-8")).hexdigest()


def auth_url_and_state(secrets: Secrets) -> tuple[str, str]:
    """Get the authorisation URL and the state.

    Args:
        secrets:
            The project secrets from the Google Developers Console.

    Returns:
        A tuple containing the generated URL and state.
    """

    state = create_state()
    url = secrets.auth_uri + (
        "?response_type=code"
        f"&client_id={secrets.client_id}"
        f"&redirect_uri={secrets.redirect_uris[0]}"
        f"&scope={'+'.join(analytix.API_SCOPES)}"
        f"&state={state}"
    )
    return url, state


def access_data_and_headers(code: str, secrets: Secrets) -> DataHeadersT:
    """Get the required data and headers for retrieving tokens from
    the YouTube Token Endpoint.

    Args:
        code:
            The authorisation code.
        secrets:
            The project secrets from the Google Developers Console.

    Returns:
        A tuple containing the data and headers.
    """

    data = {
        "client_id": secrets.client_id,
        "client_secret": secrets.client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": secrets.redirect_uris[0],
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return data, headers


def refresh_data_and_headers(token: str, secrets: Secrets) -> DataHeadersT:
    """Get the required data and headers for refreshing tokens using
    the YouTube Token Endpoint.

    Args:
        token:
            The refresh token.
        secrets:
            The project secrets from the Google Developers Console.

    Returns:
        A tuple containing the data and headers.
    """

    data = {
        "client_id": secrets.client_id,
        "client_secret": secrets.client_secret,
        "grant_type": "refresh_token",
        "refresh_token": token,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return data, headers
