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

from __future__ import annotations

import asyncio
import json
import os
import typing as t

import pytest

from analytix.tokens import Tokens
from tests.paths import SECRETS_PATH, TOKENS_PATH


@pytest.fixture()
def tokens_dict() -> dict[str, t.Any]:
    with open(TOKENS_PATH) as f:
        data = json.load(f)

    return t.cast(t.Dict[str, t.Any], data)


def test_load_from_data(tokens_dict):
    tokens = Tokens.from_data(tokens_dict)
    assert tokens.access_token == tokens_dict["access_token"]
    assert tokens.expires_in == tokens_dict["expires_in"]
    assert tokens.refresh_token == tokens_dict["refresh_token"]
    assert tokens.scope == tokens_dict["scope"]
    assert tokens.token_type == tokens_dict["token_type"]


def test_load_from_file_path_object(tokens_dict):
    tokens = Tokens.from_file(TOKENS_PATH)
    assert tokens.access_token == tokens_dict["access_token"]
    assert tokens.expires_in == tokens_dict["expires_in"]
    assert tokens.refresh_token == tokens_dict["refresh_token"]
    assert tokens.scope == tokens_dict["scope"]
    assert tokens.token_type == tokens_dict["token_type"]


def test_load_from_file_path_str(tokens_dict):
    tokens = Tokens.from_file(str(TOKENS_PATH))
    assert tokens.access_token == tokens_dict["access_token"]
    assert tokens.expires_in == tokens_dict["expires_in"]
    assert tokens.refresh_token == tokens_dict["refresh_token"]
    assert tokens.scope == tokens_dict["scope"]
    assert tokens.token_type == tokens_dict["token_type"]


def test_load_from_file_path_object_async(tokens_dict):
    tokens = asyncio.run(Tokens.afrom_file(TOKENS_PATH))
    assert tokens.access_token == tokens_dict["access_token"]
    assert tokens.expires_in == tokens_dict["expires_in"]
    assert tokens.refresh_token == tokens_dict["refresh_token"]
    assert tokens.scope == tokens_dict["scope"]
    assert tokens.token_type == tokens_dict["token_type"]


def test_load_from_file_path_str_async(tokens_dict):
    tokens = asyncio.run(Tokens.afrom_file(str(TOKENS_PATH)))
    assert tokens.access_token == tokens_dict["access_token"]
    assert tokens.expires_in == tokens_dict["expires_in"]
    assert tokens.refresh_token == tokens_dict["refresh_token"]
    assert tokens.scope == tokens_dict["scope"]
    assert tokens.token_type == tokens_dict["token_type"]


@pytest.fixture()
def tokens() -> Tokens:
    return Tokens.from_file(TOKENS_PATH)


def test_repr_output(tokens):
    output = (
        "Tokens("
        "access_token='fuie43hg984b7g0498g489gnbu4hg984bg9p74buogbwe479gnw4bg94ng4bp9gb497gb', "
        "expires_in=3599, "
        "refresh_token='gnu54ngp943bpg984npgbn480gb9483bg84b9g8b498pb', "
        "scope='https://www.googleapis.com/auth/yt-analytics-monetary.readonly https://www.googleapis.com/auth/yt-analytics.readonly', "
        "token_type='Bearer'"
        ")"
    )

    assert repr(tokens) == output
    assert f"{tokens!r}" == output


def test_getattr(tokens):
    assert tokens.access_token == tokens["access_token"]
    assert tokens.expires_in == tokens["expires_in"]
    assert tokens.refresh_token == tokens["refresh_token"]
    assert tokens.scope == tokens["scope"]
    assert tokens.token_type == tokens["token_type"]


def test_to_dict(tokens, tokens_dict):
    assert tokens.to_dict() == tokens_dict


def test_update(tokens, tokens_dict):
    tokens_dict["access_token"] = "gu985nh85n98hn430gn894hgn98"
    tokens.update(tokens_dict)
    assert tokens.access_token == tokens_dict["access_token"]
    assert tokens.access_token == "gu985nh85n98hn430gn894hgn98"
    assert tokens.expires_in == tokens_dict["expires_in"]
    assert tokens.refresh_token == tokens_dict["refresh_token"]
    assert tokens.scope == tokens_dict["scope"]
    assert tokens.token_type == tokens_dict["token_type"]


def test_write_path_object(tokens):
    tokens.write(SECRETS_PATH.parent / "test_write.json")
    assert (SECRETS_PATH.parent / "test_write.json").is_file()
    os.remove(SECRETS_PATH.parent / "test_write.json")


def test_write_path_str(tokens):
    tokens.write(str(SECRETS_PATH.parent / "test_write.json"))
    assert (SECRETS_PATH.parent / "test_write.json").is_file()
    os.remove(SECRETS_PATH.parent / "test_write.json")


def test_write_path_object_async(tokens):
    asyncio.run(tokens.awrite(SECRETS_PATH.parent / "test_write.json"))
    assert (SECRETS_PATH.parent / "test_write.json").is_file()
    os.remove(SECRETS_PATH.parent / "test_write.json")


def test_write_path_str_async(tokens):
    asyncio.run(tokens.awrite(str(SECRETS_PATH.parent / "test_write.json")))
    assert (SECRETS_PATH.parent / "test_write.json").is_file()
    os.remove(SECRETS_PATH.parent / "test_write.json")
