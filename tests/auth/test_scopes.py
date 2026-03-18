# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause


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
