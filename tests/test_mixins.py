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
            APIError, match="API returned 403: You ain't allowed in son."
        ):
            with RequestMixin()._request("https://rickroll.com"):
                ...


def test_request_api_error_ignore_errors(error_response, error_response_data):
    with mock.patch.object(PoolManager, "request", return_value=error_response):
        with RequestMixin()._request(
            "https://rickroll.com", ignore_errors=True
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
                "API returned 403: You ain't allowed in son. (probably misconfigured scopes)"
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
            "https://rickroll.com", ignore_errors=True
        ) as resp:
            assert resp.status == 503
