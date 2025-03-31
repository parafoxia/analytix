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

import datetime as dt
import json
import logging
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import Union

from analytix import utils
from analytix.errors import IdTokenError
from analytix.errors import MissingOptionalComponents
from analytix.mixins import RequestMixin
from analytix.types import PathLike

from .scopes import Scopes

if TYPE_CHECKING:
    from .secrets import Secrets

JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
OAUTH_CHECK_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo?access_token="

_log = logging.getLogger(__name__)


class _ExpiresIn(RequestMixin):
    _expires_at: dt.datetime | None = None

    def __init__(self, *, default: int = 3599) -> None:
        self._default = default

    def __get__(
        self,
        obj: Union["Tokens", None],
        objtype: type | None = None,
    ) -> float:
        if obj is None:
            return self._default

        if not self._expires_at:
            _log.debug("Looking up access token expiry time")
            with self._request(
                OAUTH_CHECK_URL + obj.access_token,
                post=True,
                ignore_errors=True,
            ) as resp:
                if resp.status >= 400:
                    _log.debug("Access token has expired")
                    return 0

                self._expires_at = dt.datetime.fromtimestamp(
                    int(json.loads(resp.data)["exp"]),
                )

        secs = max((self._expires_at - dt.datetime.now()).total_seconds(), 0)
        _log.debug("Access token is valid for another %d seconds", secs)
        return secs

    def __set__(self, obj: "Tokens", value: int) -> None:
        if self._expires_at:  # pragma: no cover
            _log.warning("Setting access token expiry time is not supported")

    def __delete__(self, obj: "Tokens") -> None:
        # Reset the expiry time.
        self._expires_at = None


@dataclass()
class Tokens(RequestMixin):
    """OAuth tokens.

    This should always be created using one of the available
    classmethods.

    ??? note "Changed in version 6.0"
        The `expires_in` attribute will now show an accurate figure
        instead of `3599` perpetually. Due to the way it's been
        implemented, it can't be updated manually.

    Attributes
    ----------
    access_token
        A token that can be sent to a Google API.
    expires_in : float
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
        provide any JWT scopes when authorising.
    """

    access_token: str
    scope: str
    token_type: Literal["Bearer"]
    refresh_token: str
    expires_in: _ExpiresIn = _ExpiresIn()
    refresh_token_expires_in: int | None = field(default=None, repr=False)
    id_token: str | None = None
    _path: Path | None = field(default=None, init=False, repr=False)

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
        _log.debug("Loading tokens from %s", tokens_file.resolve())

        self = cls.from_json(tokens_file.read_text())
        self._path = tokens_file
        return self

    @classmethod
    def from_json(cls, data: str | bytes) -> "Tokens":
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
        _log.debug("Saving tokens to %s", tokens_file.resolve())

        attrs = {
            "access_token": self.access_token,
            "expires_in": int(self.expires_in),
            "scope": self.scope,
            "token_type": self.token_type,
            "refresh_token": self.refresh_token,
            **({"id_token": self.id_token} if self.id_token else {}),
        }
        tokens_file.write_text(json.dumps(attrs))
        self._path = tokens_file

    def refresh(self, secrets: "Secrets") -> bool:
        """Refresh your access token.

        ???+ note "Changed in version 6.0"
            This now handles the refreshing of your tokens, and now
            returns a Boolean.

        Parameters
        ----------
        secrets : Secrets
            Your secrets.

        Returns
        -------
        bool
            Whether or not the refresh was successful.

        Examples
        --------
        >>> tokens.refresh(client._secrets)
        True
        """
        _log.debug("Refreshing access token")

        data = {
            "client_id": secrets.resource.client_id,
            "client_secret": secrets.resource.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        with self._request(
            secrets.resource.token_uri,
            data=data,
            headers=headers,
            ignore_errors=True,
        ) as resp:
            if resp.status > 399:
                _log.debug("Access token could not be refreshed")
                return False

            for key, value in json.loads(resp.data).items():
                setattr(self, key, value)
            del self.expires_in

            _log.debug("Access token has been refreshed successfully")
            return True

    @property
    def expired(self) -> bool:
        """Whether your access token has expired.

        !!! note "New in version 6.0"

        Returns
        -------
        bool
            Whether the token has expired or not. If it has, it needs
            refreshing.

        Examples
        --------
        >>> tokens.expired
        True
        """
        return self.expires_in == 0

    def are_scoped_for(self, scopes: Scopes) -> bool:
        """Check whether your token's scopes are sufficient.

        This cross-checks the scopes you provided the client with the
        scopes your tokens are authorised with and determines whether
        your tokens provide enough access.

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
        >>> tokens.are_scoped_for(client._scopes)
        True
        """
        sufficient = set(scopes.formatted.split(" ")) <= set(self.scope.split(" "))
        _log.debug(f"Stored scopes are {'' if sufficient else 'in'}sufficient")
        return sufficient

    @property
    def decoded_id_token(self) -> dict[str, Any] | None:
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
        >>> client = Client("secrets.json")
        >>> tokens = client.authorise()
        >>> tokens.decoded_id_token
        {
            "iss": "https://accounts.google.com",
            ...,
        }
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
