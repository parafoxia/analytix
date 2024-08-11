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
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Literal

from analytix.types import PathLike

_log = logging.getLogger(__name__)


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
