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

from analytix.errors import InvalidRequest
from analytix.reports.features import SortOptions


@pytest.fixture()
def sort_options() -> SortOptions:
    return SortOptions("views", "likes", "comments")


def test_sort_options_hash(sort_options):
    assert isinstance(hash(sort_options), int)


def test_sort_options_repr_output(sort_options):
    outputs = (
        r"SortOptions(values={'views', 'likes', 'comments'})",
        r"SortOptions(values={'views', 'comments', 'likes'})",
        r"SortOptions(values={'likes', 'views', 'comments'})",
        r"SortOptions(values={'likes', 'comments', 'views'})",
        r"SortOptions(values={'comments', 'views', 'likes'})",
        r"SortOptions(values={'comments', 'likes', 'views'})",
    )

    assert repr(sort_options) in outputs
    assert f"{sort_options!r}" in outputs


def test_sort_options_equal(sort_options):
    assert sort_options == SortOptions("views", "likes", "comments")


def test_sort_options_not_equal(sort_options):
    assert sort_options != SortOptions(
        "estimatedRevenue", "estimatedAdRevenue", "grossRevenue"
    )


def test_sort_options_valid(sort_options):
    sort_options.validate(["views", "likes", "comments"])
    sort_options.validate(["views", "-likes", "comments"])
    sort_options.validate(["-views", "-likes", "-comments"])


def test_sort_options_invalid(sort_options):
    with pytest.raises(InvalidRequest) as exc:
        sort_options.validate(["views", "likes", "henlo", "testing"])
    assert str(exc.value) in (
        "invalid sort option(s) provided: henlo, testing",
        "invalid sort option(s) provided: testing, henlo",
    )


def test_sort_options_unsupported(sort_options):
    with pytest.raises(InvalidRequest) as exc:
        sort_options.validate(["views", "likes", "dislikes", "shares"])
    assert str(exc.value) in (
        "dimensions and filters are incompatible with sort option(s): dislikes, shares",
        "dimensions and filters are incompatible with sort option(s): shares, dislikes",
    )


@pytest.fixture()
def sort_options_descending() -> SortOptions:
    return SortOptions("views", "likes", "comments", descending_only=True)


def test_sort_options_descending_valid(sort_options_descending):
    sort_options_descending.validate(["-views", "-likes", "-comments"])


def test_sort_options_descending_invalid(sort_options_descending):
    with pytest.raises(InvalidRequest) as exc:
        sort_options_descending.validate(["views", "-likes", "-comments"])
    assert (
        str(exc.value)
        in "dimensions and filters are incompatible with ascending sort options (hint: prefix with '-')"
    )
