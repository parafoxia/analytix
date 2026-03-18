# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import re

import pytest

from analytix.errors import InvalidRequest
from analytix.reports.features import SortOptions


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
        "estimatedRevenue",
        "estimatedAdRevenue",
        "grossRevenue",
    )


def test_sort_options_valid(sort_options):
    sort_options.validate(["views", "likes", "comments"])
    sort_options.validate(["views", "-likes", "comments"])
    sort_options.validate(["-views", "-likes", "-comments"])


def test_sort_options_invalid_singular(sort_options):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("invalid sort option provided: 'henlo'"),
    ):
        sort_options.validate(["views", "likes", "henlo"])


def test_sort_options_invalid_plural(sort_options):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("invalid sort options provided: 'henlo' and 'testing'"),
    ):
        sort_options.validate(["views", "likes", "henlo", "testing"])


def test_sort_options_unsupported_singular(sort_options):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "sort option 'dislikes' cannot be used with the given dimensions and filters",
        ),
    ):
        sort_options.validate(["views", "likes", "dislikes"])


def test_sort_options_unsupported_plural(sort_options):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "sort options 'dislikes' and 'shares' cannot be used with the given dimensions and filters",
        ),
    ):
        sort_options.validate(["views", "likes", "dislikes", "shares"])


def test_sort_options_descending_valid(sort_options_descending):
    sort_options_descending.validate(["-views", "-likes", "-comments"])


def test_sort_options_descending_invalid(sort_options_descending):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "dimensions and filters are incompatible with ascending sort options (hint: prefix with '-')",
        ),
    ):
        sort_options_descending.validate(["views", "-likes", "-comments"])
