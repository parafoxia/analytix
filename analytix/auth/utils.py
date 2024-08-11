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
    "auth_uri",
    "refresh_uri",
    "state_token",
    "token_uri",
)

import hashlib
import os
from urllib.parse import urlencode

from analytix.types import UriParams

from .scopes import Scopes
from .secrets import Secrets


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
    return hashlib.sha256(os.urandom(1024)).hexdigest()


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
