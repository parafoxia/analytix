# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import re

import pytest

from analytix.errors import InvalidRequest
from analytix.reports.features import Metrics


def test_metrics_hash(metrics):
    assert isinstance(hash(metrics), int)


def test_metrics_repr_output(metrics):
    outputs = (
        r"Metrics(values={'views', 'likes', 'comments'})",
        r"Metrics(values={'views', 'comments', 'likes'})",
        r"Metrics(values={'likes', 'views', 'comments'})",
        r"Metrics(values={'likes', 'comments', 'views'})",
        r"Metrics(values={'comments', 'views', 'likes'})",
        r"Metrics(values={'comments', 'likes', 'views'})",
    )

    assert repr(metrics) in outputs
    assert f"{metrics!r}" in outputs


def test_metrics_equal(metrics):
    assert metrics == Metrics("views", "likes", "comments")


def test_metrics_not_equal(metrics):
    assert metrics != Metrics("estimatedRevenue", "estimatedAdRevenue", "grossRevenue")


def test_metrics_valid(metrics):
    metrics.validate(["views", "likes", "comments"])


def test_metrics_invalid_singular(metrics):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("invalid metric provided: 'henlo'"),
    ):
        metrics.validate(["views", "likes", "henlo"])


def test_metrics_invalid_plural(metrics):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("invalid metrics provided: 'henlo' and 'testing'"),
    ):
        metrics.validate(["views", "likes", "henlo", "testing"])


def test_metrics_incompatible_singular(metrics):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "metric 'dislikes' cannot be used with the given dimensions and filters",
        ),
    ):
        metrics.validate(["views", "likes", "dislikes"])


def test_metrics_incompatible_plural(metrics):
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "metrics 'dislikes' and 'shares' cannot be used with the given dimensions and filters",
        ),
    ):
        metrics.validate(["views", "likes", "dislikes", "shares"])


def test_missing_metrics(metrics):
    with pytest.raises(
        InvalidRequest,
        match=re.escape("expected at least 1 metric, got 0"),
    ):
        metrics.validate([])
