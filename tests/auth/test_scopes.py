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


import pytest

from analytix.auth.scopes import Scopes
from analytix.errors import AuthorisationError


def test_scopes_formatting_readonly():
    assert (
        Scopes.READONLY.formatted
        == "https://www.googleapis.com/auth/yt-analytics.readonly"
    )


def test_scopes_formatting_monetary_readonly():
    assert (
        Scopes.MONETARY_READONLY.formatted
        == "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"
    )


def test_scopes_formatting_all_readonly():
    assert (
        Scopes.ALL_READONLY.formatted
        == "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly"
    )


def test_scopes_formatting_openid():
    assert Scopes.OPENID.formatted == "openid"


def test_scopes_formatting_profile():
    assert (
        Scopes.PROFILE.formatted == "https://www.googleapis.com/auth/userinfo.profile"
    )


def test_scopes_formatting_email():
    assert Scopes.EMAIL.formatted == "https://www.googleapis.com/auth/userinfo.email"


def test_scopes_formatting_all_jwt():
    assert (
        Scopes.ALL_JWT.formatted
        == "openid https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
    )


def test_scopes_formatting_all():
    assert (
        Scopes.ALL.formatted
        == "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly openid https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
    )


def test_scopes_validate_valid():
    Scopes.READONLY.validate()
    Scopes.MONETARY_READONLY.validate()
    Scopes.ALL.validate()
    (Scopes.READONLY | Scopes.OPENID).validate()


def test_scopes_validate_invalid():
    with pytest.raises(
        AuthorisationError,
        match="the READONLY or MONETARY_READONLY scope must be provided",
    ):
        Scopes.OPENID.validate()

    with pytest.raises(
        AuthorisationError,
        match="the READONLY or MONETARY_READONLY scope must be provided",
    ):
        Scopes.PROFILE.validate()

    with pytest.raises(
        AuthorisationError,
        match="the READONLY or MONETARY_READONLY scope must be provided",
    ):
        Scopes.EMAIL.validate()

    with pytest.raises(
        AuthorisationError,
        match="the READONLY or MONETARY_READONLY scope must be provided",
    ):
        Scopes.ALL_JWT.validate()
