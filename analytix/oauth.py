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

"""A module containing authorisation interfaces.

Contained here are methods through which authorisation can be performed,
and classes that represent different authorisation credentials.
Generally speaking, you won't need to call any of these functions or
instantiate any of these classes.
"""

from __future__ import annotations

__all__ = (
    "Secrets",
    "Tokens",
    "create_state",
    "auth_url_and_state",
    "access_data_and_headers",
    "refresh_data_and_headers",
)

import hashlib
import json
import logging
import pathlib
import time
import typing as t
from dataclasses import dataclass

import analytix

if t.TYPE_CHECKING:
    from analytix.types import DataHeadersT, SecretT, TokenT

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Secrets:
    """A dataclass representing a set of secrets for a Google Developers
    project.

    This should generally be created using one of the available
    classmethods.

    Parameters
    ----------
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
        match the list entered for the client ID on the API Access
        pane of the Google APIs Console.
    """

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
    def from_file(cls, path: pathlib.Path | str) -> Secrets:
        """Load a set of secrets from a file downloaded from the Google
        Developers Console.

        Parameters
        ----------
        path : Path object or str
            The path to the secrets file.

        Returns
        -------
        Secrets
            An instance representing your secrets.
        """

        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        _log.debug(f"Loading secrets from {path.resolve()}...")

        with open(path) as f:
            data = json.load(f)["installed"]

        _log.info("Secrets loaded!")
        return cls(**data)

    def to_dict(self) -> dict[str, SecretT]:
        """Convert secrets to a dictionary.

        Parameters
        ----------
        dict of secrets
            A dictionary of secrets, where the keys are strings, and the
            values are either strings or lists of strings.
        """

        return {
            "client_id": self.client_id,
            "project_id": self.project_id,
            "auth_uri": self.auth_uri,
            "token_uri": self.token_uri,
            "auth_provider_x509_cert_url": self.auth_provider_x509_cert_url,
            "client_secret": self.client_secret,
            "redirect_uris": self.redirect_uris,
        }


@dataclass()
class Tokens:
    """A dataclass representing a set of tokens for a Google Developers
    project.

    This should generally be created using one of the available
    classmethods.

    Parameters
    ----------
    access_token : str
        The token used to access services.
    expires_in : int
        The number of seconds until the token expires. This is not live
        updated by analytix, and so should not be used to track a
        token's expiration.
    refresh_token : str
        The token used to refresh the access token.
    scope : str
        The scopes the token is authorised for. This is provided as a
        single string, where separate scopes are separated by a space.
    token_type : str
        The type of token. Will probably be "Bearer".
    """

    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str

    def __getitem__(self, key: str) -> TokenT:
        return t.cast(TokenT, getattr(self, key))

    @classmethod
    def from_json(cls, data: dict[str, TokenT]) -> Tokens:
        """Create an instance of this class from a dictionary.

        Parameters
        ----------
        data : dict of tokens
            The tokens as a dictionary.

        Returns
        -------
        Tokens
            An instance representing your tokens.
        """

        return cls(**data)  # type: ignore

    @classmethod
    def from_file(cls, path: pathlib.Path | str) -> Tokens:
        """Load a set of tokens from a file generated by analytix.

        Parameters
        ----------
        path : Path object or str
            The path to the tokens file.

        Returns
        -------
        Tokens
            An instance representing your tokens.
        """

        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        _log.debug(f"Loading tokens from {path.resolve()}...")

        with open(path) as f:
            data = json.load(f)

        _log.info("Tokens loaded!")
        return cls(**data)

    def to_dict(self) -> dict[str, TokenT]:
        """Convert tokens to a dictionary.

        Returns
        -------
        dict of tokens
            A dictionary of tokens, where the keys are strings, and the
            values are either strings or integers.
        """

        return {
            "access_token": self.access_token,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "token_type": self.token_type,
        }

    def update(self, data: dict[str, TokenT]) -> None:
        """Update token attributes.

        Parameters
        ----------
        data : dict of tokens
            A dictionary of attributes to be updated.

        !!! note
            This does not update the tokens on disk.
        """

        for k, v in data.items():
            setattr(self, k, v)

        _log.info("Tokens updated!")

    def write(self, path: pathlib.Path | str) -> None:
        """Write tokens to a file.

        Parameters
        ----------
        path : Path object or str
            The path to the tokens file.
        """

        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        with open(path, "w") as f:
            json.dump(self.to_dict(), f)

        _log.info(f"Tokens saved to {path.resolve()}")


def create_state() -> str:
    """Create a random state for requests.

    Returns
    -------
    str
        The state as a 64-character long hexadecimal string.
    """

    return hashlib.sha256(f"{time.time()}".encode("utf-8")).hexdigest()


def auth_url_and_state(secrets: Secrets, redirect_uri: str) -> tuple[str, str]:
    """Get the authorisation URL and the state.

    Parameters
    ----------
    secrets : Secrets
        The project secrets from the Google Developers Console.
    redirect_uri : str
        The URI to redirect to after authorisation.

    Returns
    -------
    tuple of str
        A tuple containing the generated URL and state.
    """

    state = create_state()
    url = secrets.auth_uri + (
        "?response_type=code"
        f"&client_id={secrets.client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={'+'.join(analytix.API_SCOPES)}"
        f"&state={state}"
    )
    return url, state


def access_data_and_headers(
    code: str, secrets: Secrets, redirect_uri: str
) -> DataHeadersT:
    """Get the required data and headers for retrieving tokens from
    the YouTube Token Endpoint.

    Parameters
    ----------
    code : str
        The authorisation code.
    secrets : Secrets
        The project secrets from the Google Developers Console.
    redirect_uri : str
        The URI to redirect to after authorisation.

    Returns
    -------
    tuple of dicts (each str-str)
        A tuple containing the data and headers.
    """

    data = {
        "client_id": secrets.client_id,
        "client_secret": secrets.client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return data, headers


def refresh_data_and_headers(token: str, secrets: Secrets) -> DataHeadersT:
    """Get the required data and headers for refreshing tokens using
    the YouTube Token Endpoint.

    Parameters
    ----------
    token : str
        The refresh token.
    secrets : Secrets
        The project secrets from the Google Developers Console.

    Returns
    -------
    tuple of dicts (each str-str)
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
