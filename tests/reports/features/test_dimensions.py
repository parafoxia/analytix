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
    Dimensions,
    ExactlyOne,
    OneOrMore,
    Optional,
    Required,
    ZeroOrMore,
    ZeroOrOne,
)


def test_dimensions_every(dimensions_required):
    assert dimensions_required.every in ({"day", "month"}, {"month", "day"})


def test_dimensions_invalid_singular(dimensions_required):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("invalid dimension provided: 'henlo'"),
    ):
        dimensions_required.validate(["day", "month", "henlo"])


def test_dimensions_invalid_plural(dimensions_required):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("invalid dimensions provided: 'henlo' and 'testing'"),
    ):
        dimensions_required.validate(["day", "month", "henlo", "testing"])


def test_dimensions_unsupported(dimensions_required):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "dimensions 'country', 'day', and 'month' cannot be used together"
        ),
    ):
        dimensions_required.validate(["day", "month", "country"])


def test_dimensions_hash(dimensions_required):
    assert isinstance(hash(dimensions_required), int)


# -----


def test_dimensions_required_repr_output(dimensions_required):
    outputs = (
        r"Dimensions(values={Required(values={'day', 'month'})})",
        r"Dimensions(values={Required(values={'month', 'day'})})",
    )

    assert repr(dimensions_required) in outputs
    assert f"{dimensions_required!r}" in outputs


def test_dimensions_required_equal(dimensions_required):
    assert dimensions_required == Dimensions(Required("day", "month"))


def test_dimensions_required_not_equal(dimensions_required):
    assert dimensions_required != Dimensions(Required("country", "subContinent"))


def test_dimensions_required_valid(dimensions_required):
    dimensions_required.validate(["day", "month"])


def test_dimensions_required_invalid_set(dimensions_required):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("expected all dimensions from 'day' and 'month', got 1"),
    ):
        dimensions_required.validate(["day"])


def test_dimensions_exactly_one_repr_output(dimensions_exactly_one):
    outputs = (
        r"Dimensions(values={ExactlyOne(values={'day', 'month'})})",
        r"Dimensions(values={ExactlyOne(values={'month', 'day'})})",
    )

    assert repr(dimensions_exactly_one) in outputs
    assert f"{dimensions_exactly_one!r}" in outputs


def test_dimensions_exactly_one_equal(dimensions_exactly_one):
    assert dimensions_exactly_one == Dimensions(ExactlyOne("day", "month"))


def test_dimensions_exactly_one_not_equal(dimensions_required, dimensions_exactly_one):
    assert dimensions_required != dimensions_exactly_one


def test_dimensions_exactly_one_valid(dimensions_exactly_one):
    dimensions_exactly_one.validate(["day"])
    dimensions_exactly_one.validate(["month"])


def test_dimensions_exactly_one_invalid_set_zero(dimensions_exactly_one):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("expected 1 dimension from 'day' and 'month', got 0"),
    ):
        dimensions_exactly_one.validate([])


def test_dimensions_exactly_one_invalid_set_two(dimensions_exactly_one):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "expected 1 dimension from 'day' and 'month', got 2",
        ),
    ):
        dimensions_exactly_one.validate(["day", "month"])


def test_dimensions_one_or_more_repr_output(dimensions_one_or_more):
    outputs = (
        r"Dimensions(values={OneOrMore(values={'day', 'month'})})",
        r"Dimensions(values={OneOrMore(values={'month', 'day'})})",
    )

    assert repr(dimensions_one_or_more) in outputs
    assert f"{dimensions_one_or_more!r}" in outputs


def test_dimensions_one_or_more_equal(dimensions_one_or_more):
    assert dimensions_one_or_more == Dimensions(OneOrMore("day", "month"))


def test_dimensions_one_or_more_not_equal(dimensions_required, dimensions_one_or_more):
    assert dimensions_required != dimensions_one_or_more


def test_dimensions_one_or_more_valid(dimensions_one_or_more):
    dimensions_one_or_more.validate(["day"])
    dimensions_one_or_more.validate(["month"])
    dimensions_one_or_more.validate(["day", "month"])


def test_dimensions_one_or_more_invalid_set_zero(dimensions_one_or_more):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "expected at least 1 dimension from 'day' and 'month', got 0",
        ),
    ):
        dimensions_one_or_more.validate([])


def test_dimensions_optional_repr_output(dimensions_optional):
    outputs = (
        r"Dimensions(values={Optional(values={'day', 'month'})})",
        r"Dimensions(values={Optional(values={'month', 'day'})})",
    )

    assert repr(dimensions_optional) in outputs
    assert f"{dimensions_optional!r}" in outputs


def test_dimensions_optional_equal(dimensions_optional):
    assert dimensions_optional == Dimensions(Optional("day", "month"))


def test_dimensions_optional_not_equal(dimensions_required, dimensions_optional):
    assert dimensions_required != dimensions_optional


def test_dimensions_optional_valid(dimensions_optional):
    dimensions_optional.validate([])
    dimensions_optional.validate(["day"])
    dimensions_optional.validate(["month"])
    dimensions_optional.validate(["day", "month"])


def test_dimensions_zero_or_one_repr_output(dimensions_zero_or_one):
    outputs = (
        r"Dimensions(values={ZeroOrOne(values={'day', 'month'})})",
        r"Dimensions(values={ZeroOrOne(values={'month', 'day'})})",
    )

    assert repr(dimensions_zero_or_one) in outputs
    assert f"{dimensions_zero_or_one!r}" in outputs


def test_dimensions_zero_or_one_equal(dimensions_zero_or_one):
    assert dimensions_zero_or_one == Dimensions(ZeroOrOne("day", "month"))


def test_dimensions_zero_or_one_not_equal(dimensions_required, dimensions_zero_or_one):
    assert dimensions_required != dimensions_zero_or_one


def test_dimensions_zero_or_one_valid(dimensions_zero_or_one):
    dimensions_zero_or_one.validate(["day"])
    dimensions_zero_or_one.validate(["month"])
    dimensions_zero_or_one.validate([])


def test_dimensions_zero_or_one_invalid_set_two(dimensions_zero_or_one):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "expected 0 or 1 dimensions from 'day' and 'month', got 2",
        ),
    ):
        dimensions_zero_or_one.validate(["day", "month"])


def test_dimensions_zero_or_more_repr_output(dimensions_zero_or_more):
    outputs = (
        r"Dimensions(values={ZeroOrMore(values={'day', 'month'})})",
        r"Dimensions(values={ZeroOrMore(values={'month', 'day'})})",
    )

    assert repr(dimensions_zero_or_more) in outputs
    assert f"{dimensions_zero_or_more!r}" in outputs


def test_dimensions_zero_or_more_equal(dimensions_zero_or_more):
    assert dimensions_zero_or_more == Dimensions(ZeroOrMore("day", "month"))


def test_dimensions_zero_or_more_not_equal(
    dimensions_required, dimensions_zero_or_more
):
    assert dimensions_required != dimensions_zero_or_more


def test_dimensions_zero_or_more_valid(dimensions_zero_or_more):
    dimensions_zero_or_more.validate([])
    dimensions_zero_or_more.validate(["day"])
    dimensions_zero_or_more.validate(["month"])
    dimensions_zero_or_more.validate(["day", "month"])
