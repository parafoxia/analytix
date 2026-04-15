# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

__all__ = ("Scopes",)

from enum import Flag

from analytix.errors import AuthorisationError

SCOPE_URLS = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]


class Scopes(Flag):
    """An enum for API scopes.

    Possible values are:

    * `READONLY` — Don't include revenue data from reports
    * `MONETARY_READONLY` — Only include revenue data from reports
    * `ALL_READONLY` — Include all data in reports
    * `OPENID` — Enable the OpenID scope
    * `PROFILE` — Include profile information in JWTs
    * `EMAIL` — Include email information in JWTs
    * `ALL_JWT` — Include all available information in JWTs
    * `ALL` — Include all data in reports

    ???+ note "Changed in version 6.0"
        The `ALL_READONLY` scope has been added and mimics the behaviour
        of the `ALL` scope from v5. The `ALL` scope now includes all JWT
        scopes.

    ???+ note "Changed in version 5.1"
        * Added the `OPENID`, `PROFILE`, `EMAIL`, and `ALL_JWT` scopes
        * This now works like a flag enum rather than a normal one; this
          doesn't introduce any breaking changes (unless you're using
          analytix in a particularly unconventional way), but does mean
          you can now use a `|` to concatenate scopes
    """

    READONLY = 1 << 0
    MONETARY_READONLY = 1 << 1
    ALL_READONLY = READONLY | MONETARY_READONLY
    OPENID = 1 << 2
    PROFILE = 1 << 3
    EMAIL = 1 << 4
    ALL_JWT = OPENID | PROFILE | EMAIL
    ALL = ALL_READONLY | ALL_JWT

    @property
    def formatted(self) -> str:
        return " ".join(
            url for i, url in enumerate(SCOPE_URLS) if self.value & (1 << i)
        )

    def validate(self) -> None:
        if not (self.value & (1 << 0) or self.value & (1 << 1)):
            raise AuthorisationError(
                "the READONLY or MONETARY_READONLY scope must be provided",
            )
