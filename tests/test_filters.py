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

from analytix import errors
from analytix.features import (
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


def test_filters_invalid(filters_required):
    with pytest.raises(errors.InvalidFilters) as exc:
        filters_required.validate(
            {
                "country": "US",
                "video": "nf94bg4b397gb",
                "henlo": "yolo",
                "testing": "123",
            }
        )
    assert str(exc.value) in (
        "invalid filter(s) provided: henlo, testing",
        "invalid filter(s) provided: testing, henlo",
    )


def test_filters_unsupported(filters_required):
    with pytest.raises(errors.UnsupportedFilters) as exc:
        filters_required.validate(
            {"country": "US", "video": "nf94bg4b397gb", "group": "nf74ng984b98g"}
        )
    assert str(exc.value) == "unsupported filter(s) for selected report type: group"


def test_filters_invalid_value(filters_required):
    with pytest.raises(errors.InvalidFilterValue) as exc:
        filters_required.validate({"country": "UK", "video": "nf94bg4b397gb"})
    assert str(exc.value) == "invalid value for filter 'country': 'UK'"


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
    with pytest.raises(errors.UnsupportedFilterValue) as exc:
        filters_required_locked.validate({"country": "GB", "video": "nf94bg4b397gb"})
    assert (
        str(exc.value)
        == "unsupported value for filter 'country' for selected report type: 'GB'"
    )


def test_filters_required_repr_output(filters_required):
    outputs = (
        r"Filters(values={Required(values={'country', 'video'})})",
        r"Filters(values={Required(values={'video', 'country'})})",
    )

    assert repr(filters_required) in outputs
    assert f"{filters_required!r}" in outputs


def test_filters_equal(filters_required):
    assert filters_required == Filters(Required("country", "video"))


def test_filters_not_equal(filters_required):
    assert filters_required != Filters(Required("country", "subContinent"))


def test_filters_not_equal_required(filters_required):
    assert filters_required != Filters(Required("country", "subContinent"))


def test_filters_required(filters_required):
    filters_required.validate({"country": "US", "video": "nf94bg4b397gb"})


def test_filters_required_invalid_set(filters_required):
    with pytest.raises(errors.InvalidSetOfFilters) as exc:
        filters_required.validate({"country": "US"})
    assert str(exc.value) in (
        "expected all filter(s) from 'country, video', got 1",
        "expected all filter(s) from 'video, country', got 1",
    )


@pytest.fixture()
def filters_exactly_one() -> Filters:
    return Filters(ExactlyOne("country", "video"))


def test_filters_not_equal_exactly_one(filters_required, filters_exactly_one):
    assert filters_required != filters_exactly_one


def test_filters_exactly_one_repr_output(filters_exactly_one):
    outputs = (
        r"Filters(values={ExactlyOne(values={'country', 'video'})})",
        r"Filters(values={ExactlyOne(values={'video', 'country'})})",
    )

    assert repr(filters_exactly_one) in outputs
    assert f"{filters_exactly_one!r}" in outputs


def test_filters_exactly_one(filters_exactly_one):
    filters_exactly_one.validate({"country": "US"})
    filters_exactly_one.validate({"video": "nf94bg4b397gb"})


def test_filters_exactly_one_invalid_set_zero(filters_exactly_one):
    with pytest.raises(errors.InvalidSetOfFilters) as exc:
        filters_exactly_one.validate({})
    assert str(exc.value) in (
        "expected 1 filter(s) from 'country, video', got 0",
        "expected 1 filter(s) from 'video, country', got 0",
    )


def test_filters_exactly_one_invalid_set_two(filters_exactly_one):
    with pytest.raises(errors.InvalidSetOfFilters) as exc:
        filters_exactly_one.validate({"country": "US", "video": "nf94bg4b397gb"})
    assert str(exc.value) in (
        "expected 1 filter(s) from 'country, video', got 2",
        "expected 1 filter(s) from 'video, country', got 2",
    )


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


def test_filters_one_or_more(filters_one_or_more):
    filters_one_or_more.validate({"country": "US"})
    filters_one_or_more.validate({"video": "nf94bg4b397gb"})
    filters_one_or_more.validate({"country": "US", "video": "nf94bg4b397gb"})


def test_filters_one_or_more_invalid_set_zero(filters_one_or_more):
    with pytest.raises(errors.InvalidSetOfFilters) as exc:
        filters_one_or_more.validate({})
    assert str(exc.value) in (
        "expected at least 1 filter(s) from 'country, video', got 0",
        "expected at least 1 filter(s) from 'video, country', got 0",
    )


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


def test_filters_optional(filters_optional):
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


def test_filters_zero_or_one(filters_zero_or_one):
    filters_zero_or_one.validate({})
    filters_zero_or_one.validate({"country": "US"})
    filters_zero_or_one.validate({"video": "nf94bg4b397gb"})


def test_filters_zero_or_one_invalid_set_two(filters_zero_or_one):
    with pytest.raises(errors.InvalidSetOfFilters) as exc:
        filters_zero_or_one.validate({"country": "US", "video": "nf94bg4b397gb"})
    assert str(exc.value) in (
        "expected 0 or 1 filter(s) from 'country, video', got 2",
        "expected 0 or 1 filter(s) from 'video, country', got 2",
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


def test_filters_zero_or_more(filters_zero_or_more):
    filters_zero_or_more.validate({})
    filters_zero_or_more.validate({"country": "US"})
    filters_zero_or_more.validate({"video": "nf94bg4b397gb"})
    filters_zero_or_more.validate({"country": "US", "video": "nf94bg4b397gb"})
