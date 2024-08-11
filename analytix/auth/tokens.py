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
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional
from typing import Union

from analytix import utils
from analytix.errors import APIError
from analytix.errors import IdTokenError
from analytix.errors import MissingOptionalComponents
from analytix.mixins import RequestMixin
from analytix.types import PathLike

from .scopes import Scopes

JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
OAUTH_CHECK_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo?access_token="

_log = logging.getLogger(__name__)


@dataclass(**({"slots": True} if sys.version_info >= (3, 10) else {}))
class Tokens(RequestMixin):
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
    _path: Optional[Path] = field(default=None, init=False, repr=False)

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

        self = cls.from_json(tokens_file.read_text())
        self._path = tokens_file
        return self

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
        self._path = tokens_file

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

    @property
    def are_valid(self) -> bool:
        """Whether your access token is valid.

        The default implementation makes a call to Google's OAuth2 API
        to determine the token's validity.

        !!! note "New in version 6.0"

        Returns
        -------
        bool
            Whether the token is valid or not. If it isn't, it needs
            refreshing.

        Examples
        --------
        >>> token.are_valid
        True
        """
        try:
            with self._request(OAUTH_CHECK_URL + self.access_token, post=True):
                _log.debug("Access token does not need refreshing")
                return True
        except APIError:
            _log.debug("Access token needs refreshing")
            return False

    def are_scoped_for(self, scopes: Scopes) -> bool:
        """Check whether your token's scopes are sufficient.

        This cross-checks the scopes you provided the client with the
        scopes your tokens are authorised with and determines whether
        your tokens provide enough access.

        This is not an equality check; if your tokens are authorised
        with all scopes, but you only passed the READONLY scope to the
        client, this will return `True`.

        !!! note "New in version 6.0"

        Parameters
        ----------
        scopes
            Your client's scopes.

        Returns
        -------
        bool
            Whether the scopes are sufficient or not. If they're not,
            you'll need to reauthorise.

        Examples
        --------
        >>> tokens.are_scopes_for(client.scopes)
        True
        """
        sufficient = set(scopes.formatted.split(" ")) <= set(self.scope.split(" "))
        _log.debug(f"Stored scopes are {'' if sufficient else 'in'}sufficient")
        return sufficient

    @property
    def decoded_id_token(self) -> Optional[Dict[str, Any]]:
        """The decoded ID token.

        ID tokens are returned from the YouTube Analytics API as a JWT,
        which is a secure way to transfer encrypted JSON objects. This
        property decrypts and decodes the JWT and returns the stored
        information.

        !!! note "New in version 6.0"

        Returns
        -------
        Optional[Dict[str, Any]]
            The decoded ID token, or `None` if there is no ID token.

        Raises
        ------
        MissingOptionalComponents
            python-jwt is not installed.
        IdTokenError
            Your ID token could not be decoded. This may be raised
            alongside other errors.

        Notes
        -----
        This requires `jwt` to be installed to use, which is an optional
        dependency.

        Examples
        --------
        >>> client = BaseClient("secrets.json")
        >>> tokens = client.authorise()  # Overloaded using your impl.
        >>> tokens.decoded_id_token
        """
        if not self.id_token:
            return None

        if not utils.can_use("jwt"):
            raise MissingOptionalComponents("jwt")

        from jwt import JWT
        from jwt import jwk_from_dict
        from jwt.exceptions import JWSDecodeError

        _log.debug("Fetching JWKs")
        with self._request(JWKS_URI) as resp:
            if resp.status > 399:
                raise IdTokenError("could not fetch Google JWKs")

            keys = json.loads(resp.data)["keys"]

        jwt = JWT()  # type: ignore[no-untyped-call]

        for key in keys:
            jwk = jwk_from_dict(key)
            _log.debug("Attempting decode using JWK with KID %r", jwk.get_kid())
            try:
                return jwt.decode(self.id_token, jwk)
            except Exception as exc:
                if not isinstance(exc.__cause__, JWSDecodeError):
                    # If the error IS a JWSDecodeError, we want to try
                    # other keys and error later if they also fail.
                    raise IdTokenError("invalid ID token (see above error)") from exc

        raise IdTokenError("ID token signature could not be validated")
