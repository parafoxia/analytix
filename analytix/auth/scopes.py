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
