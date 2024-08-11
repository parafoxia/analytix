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

__all__ = ("Tokens",)

import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from typing import Optional
from typing import Union

from analytix.types import PathLike

_log = logging.getLogger(__name__)


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
