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

import pytest

from analytix.errors import InvalidRequest
from analytix.reports.features import (
    ExactlyOne,
    Filters,
    OneOrMore,
    Optional,
    Required,
    ZeroOrMore,
    ZeroOrOne,
)


@pytest.fixture()
def filters_required() -> Filters:
    return Filters(Required("country", "video"))


def test_filters_every(filters_required):
    assert filters_required.every in ({"country", "video"}, {"video", "country"})


def test_filters_every_key(filters_required):
    assert filters_required.every_key in ({"country", "video"}, {"video", "country"})


def test_filters_locked(filters_required):
    assert filters_required.locked == {}


def test_filters_invalid_singular(filters_required):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("invalid filter provided: 'henlo'"),
    ):
        filters_required.validate(
            {
                "country": "US",
                "video": "nf94bg4b397gb",
                "henlo": "yolo",
            }
        )


def test_filters_invalid_plural(filters_required):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("invalid filters provided: 'henlo' and 'testing'"),
    ):
        filters_required.validate(
            {
                "country": "US",
                "video": "nf94bg4b397gb",
                "henlo": "yolo",
                "testing": "123",
            }
        )


def test_filters_unsupported(filters_required):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "filters 'country', 'group', and 'video' cannot be used together"
        ),
    ):
        filters_required.validate(
            {"country": "US", "video": "nf94bg4b397gb", "group": "nf74ng984b98g"}
        )


def test_filters_invalid_value(filters_required):
    with pytest.raises(
        InvalidRequest, match=re.escape("invalid value 'UK' for filter 'country'")
    ):
        filters_required.validate({"country": "UK", "video": "nf94bg4b397gb"})


@pytest.fixture()
def filters_required_locked() -> Filters:
    return Filters(Required("country==US", "video"))


def test_filters_locked_every(filters_required_locked):
    assert filters_required_locked.every in (
        {"country==US", "video"},
        {"video", "country==US"},
    )


def test_filters_locked_every_key(filters_required_locked):
    assert filters_required_locked.every_key in (
        {"country", "video"},
        {"video", "country"},
    )


def test_filters_locked_locked(filters_required_locked):
    assert filters_required_locked.locked == {"country": "US"}


def test_filters_unsupported_value(filters_required_locked):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "value 'GB' for filter 'country' cannot be used with the given dimensions"
        ),
    ):
        filters_required_locked.validate({"country": "GB", "video": "nf94bg4b397gb"})


def test_filters_hash(filters_required):
    assert isinstance(hash(filters_required), int)


# -----


def test_filters_required_repr_output(filters_required):
    outputs = (
        r"Filters(values={Required(values={'country', 'video'})})",
        r"Filters(values={Required(values={'video', 'country'})})",
    )

    assert repr(filters_required) in outputs
    assert f"{filters_required!r}" in outputs


def test_filters_required_equal(filters_required):
    assert filters_required == Filters(Required("country", "video"))


def test_filters_required_not_equal(filters_required):
    assert filters_required != Filters(Required("country", "subContinent"))


def test_filters_required_valid(filters_required):
    filters_required.validate({"country": "US", "video": "nf94bg4b397gb"})


def test_filters_required_invalid_set(filters_required):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "expected all filters from 'country' and 'video', got 1",
        ),
    ):
        filters_required.validate({"country": "US"})


@pytest.fixture()
def filters_exactly_one() -> Filters:
    return Filters(ExactlyOne("country", "video"))


def test_filters_exactly_one_repr_output(filters_exactly_one):
    outputs = (
        r"Filters(values={ExactlyOne(values={'country', 'video'})})",
        r"Filters(values={ExactlyOne(values={'video', 'country'})})",
    )

    assert repr(filters_exactly_one) in outputs
    assert f"{filters_exactly_one!r}" in outputs


def test_filters_exactly_one_equal(filters_exactly_one):
    assert filters_exactly_one == Filters(ExactlyOne("country", "video"))


def test_filters_exactly_one_not_equal(filters_required, filters_exactly_one):
    assert filters_required != filters_exactly_one


def test_filters_exactly_one_valid(filters_exactly_one):
    filters_exactly_one.validate({"country": "US"})
    filters_exactly_one.validate({"video": "nf94bg4b397gb"})


def test_filters_exactly_one_invalid_set_zero(filters_exactly_one):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "expected 1 filter from 'country' and 'video', got 0",
        ),
    ):
        filters_exactly_one.validate({})


def test_filters_exactly_one_invalid_set_two(filters_exactly_one):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "expected 1 filter from 'country' and 'video', got 2",
        ),
    ):
        filters_exactly_one.validate({"country": "US", "video": "nf94bg4b397gb"})


@pytest.fixture()
def filters_one_or_more() -> Filters:
    return Filters(OneOrMore("country", "video"))


def test_filters_one_or_more_repr_output(filters_one_or_more):
    outputs = (
        r"Filters(values={OneOrMore(values={'country', 'video'})})",
        r"Filters(values={OneOrMore(values={'video', 'country'})})",
    )

    assert repr(filters_one_or_more) in outputs
    assert f"{filters_one_or_more!r}" in outputs


def test_filters_one_or_more_equal(filters_one_or_more):
    assert filters_one_or_more == Filters(OneOrMore("country", "video"))


def test_filters_one_or_more_not_equal(filters_required, filters_one_or_more):
    assert filters_required != filters_one_or_more


def test_filters_one_or_more_valid(filters_one_or_more):
    filters_one_or_more.validate({"country": "US"})
    filters_one_or_more.validate({"video": "nf94bg4b397gb"})
    filters_one_or_more.validate({"country": "US", "video": "nf94bg4b397gb"})


def test_filters_one_or_more_invalid_set_zero(filters_one_or_more):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "expected at least 1 filter from 'country' and 'video', got 0",
        ),
    ):
        filters_one_or_more.validate({})


@pytest.fixture()
def filters_optional() -> Filters:
    return Filters(Optional("country", "video"))


def test_filters_optional_repr_output(filters_optional):
    outputs = (
        r"Filters(values={Optional(values={'country', 'video'})})",
        r"Filters(values={Optional(values={'video', 'country'})})",
    )

    assert repr(filters_optional) in outputs
    assert f"{filters_optional!r}" in outputs


def test_filters_optional_equal(filters_optional):
    assert filters_optional == Filters(Optional("country", "video"))


def test_filters_optional_not_equal(filters_required, filters_optional):
    assert filters_required != filters_optional


def test_filters_optional_valid(filters_optional):
    filters_optional.validate({})
    filters_optional.validate({"country": "US"})
    filters_optional.validate({"video": "nf94bg4b397gb"})
    filters_optional.validate({"country": "US", "video": "nf94bg4b397gb"})


@pytest.fixture()
def filters_zero_or_one() -> Filters:
    return Filters(ZeroOrOne("country", "video"))


def test_filters_zero_or_one_repr_output(filters_zero_or_one):
    outputs = (
        r"Filters(values={ZeroOrOne(values={'country', 'video'})})",
        r"Filters(values={ZeroOrOne(values={'video', 'country'})})",
    )

    assert repr(filters_zero_or_one) in outputs
    assert f"{filters_zero_or_one!r}" in outputs


def test_filters_zero_or_one_equal(filters_zero_or_one):
    assert filters_zero_or_one == Filters(ZeroOrOne("country", "video"))


def test_filters_zero_or_one_not_equal(filters_required, filters_zero_or_one):
    assert filters_required != filters_zero_or_one


def test_filters_zero_or_one_valid(filters_zero_or_one):
    filters_zero_or_one.validate({})
    filters_zero_or_one.validate({"country": "US"})
    filters_zero_or_one.validate({"video": "nf94bg4b397gb"})


def test_filters_zero_or_one_invalid_set_two(filters_zero_or_one):
    with pytest.raises(InvalidRequest) as exc:
        filters_zero_or_one.validate({"country": "US", "video": "nf94bg4b397gb"})
    assert str(exc.value) in (
        "expected 0 or 1 filters from 'country' and 'video', got 2",
    )


@pytest.fixture()
def filters_zero_or_more() -> Filters:
    return Filters(ZeroOrMore("country", "video"))


def test_filters_zero_or_more_repr_output(filters_zero_or_more):
    outputs = (
        r"Filters(values={ZeroOrMore(values={'country', 'video'})})",
        r"Filters(values={ZeroOrMore(values={'video', 'country'})})",
    )

    assert repr(filters_zero_or_more) in outputs
    assert f"{filters_zero_or_more!r}" in outputs


def test_filters_zero_or_more_equal(filters_zero_or_more):
    assert filters_zero_or_more == Filters(ZeroOrMore("country", "video"))


def test_filters_zero_or_more_not_equal(filters_required, filters_zero_or_more):
    assert filters_required != filters_zero_or_more


def test_filters_zero_or_more_valid(filters_zero_or_more):
    filters_zero_or_more.validate({})
    filters_zero_or_more.validate({"country": "US"})
    filters_zero_or_more.validate({"video": "nf94bg4b397gb"})
    filters_zero_or_more.validate({"country": "US", "video": "nf94bg4b397gb"})
