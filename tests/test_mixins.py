# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import re
from unittest import mock

import pytest
from urllib3 import PoolManager
from urllib3.exceptions import MaxRetryError

from analytix.errors import APIError
from analytix.mixins import RequestMixin


def test_request(response, response_data):
    with mock.patch.object(PoolManager, "request", return_value=response):
        with RequestMixin()._request("https://rickroll.com") as resp:
            assert resp.status == 200
            assert resp.data == response_data


def test_request_api_error(error_response):
    with mock.patch.object(PoolManager, "request", return_value=error_response):
        with pytest.raises(
            APIError,
            match="API returned 403: You ain't allowed in son.",
        ):
            with RequestMixin()._request("https://rickroll.com"):
                ...


def test_request_api_error_ignore_errors(error_response, error_response_data):
    with mock.patch.object(PoolManager, "request", return_value=error_response):
        with RequestMixin()._request(
            "https://rickroll.com",
            ignore_errors=True,
        ) as resp:
            assert resp.status == 403
            assert resp.reason == "You ain't allowed in son."
            assert resp.data == error_response_data


def test_request_with_access_token(response, tokens):
    with mock.patch.object(PoolManager, "request", return_value=response):
        with RequestMixin()._request("https://rickroll.com", token=tokens.access_token):
            # There's not really any way to test if the headers were
            # passed, though we can double-check against the coverage
            # to ensure the operation was at least attempted.
            ...


def test_request_forbidden_error_additional_context(error_response):
    with mock.patch.object(PoolManager, "request", return_value=error_response):
        with pytest.raises(
            APIError,
            match=re.escape(
                "API returned 403: You ain't allowed in son. (probably misconfigured scopes)",
            ),
        ):
            with RequestMixin()._request("https://rickroll.com/v2/reports"):
                ...


def test_request_time_out():
    with mock.patch.object(PoolManager, "request", side_effect=MaxRetryError(None, "")):
        with pytest.raises(MaxRetryError):
            with RequestMixin()._request("https://rickroll.com"):
                ...


def test_request_time_out_ignore_errors():
    with mock.patch.object(PoolManager, "request", side_effect=MaxRetryError(None, "")):
        with RequestMixin()._request(
            "https://rickroll.com",
            ignore_errors=True,
        ) as resp:
            assert resp.status == 503
