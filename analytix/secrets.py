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

import json
import logging
import pathlib
import typing as t
from dataclasses import dataclass

import aiofiles

from analytix.types import SecretT

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Secrets:
    """A dataclass representing a set of secrets for a Google Developers
    project. This should generally be created using one of the available
    classmethods.

    Args:
        client_id:
            The client ID.
        project_id:
            The name of the project.
        auth_uri:
            The authorisation server endpoint URI.
        token_uri:
            The token server endpoint URI.
        auth_provider_x509_cert_url:
            The URL of the public x509 certificate, used to verify the
            signature on JWTs, such as ID tokens, signed by the
            authentication provider.
        client_secret:
            The client secret.
        redirect_uris:
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

        Args:
            path:
                The path to the secrets file.

        Returns:
            The loaded secrets.
        """

        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        log.debug(f"Loading secrets from {path.resolve()}...")

        with open(path) as f:
            data = json.load(f)["installed"]

        log.info("Secrets loaded!")
        return cls(**data)

    @classmethod
    async def afrom_file(cls, path: pathlib.Path | str) -> Secrets:
        """Asynchronously load a set of secrets from a file downloaded
        from the Google Developers Console.

        Args:
            path:
                The path to the secrets file.

        Returns:
            The loaded secrets.
        """

        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        log.debug(f"Loading secrets from {path.resolve()}...")

        async with aiofiles.open(path) as f:
            data = json.loads(await f.read())["installed"]

        log.info("Secrets loaded!")
        return cls(**data)

    def to_dict(self) -> dict[str, SecretT]:
        """Convert secrets to a dictionary.

        Returns:
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
