# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from analytix.errors import InvalidRequest
from analytix.reports import data
from analytix.reports import types as rt


def test_str_output():
    report = rt.BasicUserActivity()
    assert str(report) == "Basic user activity"


def test_detailed_report_no_max_results():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "insightPlaybackLocationType": "EMBEDDED",
        "country": "US",
        "video": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    with pytest.raises(InvalidRequest) as exc:
        report.validate(d, f, m, s, 0)
    assert str(exc.value) == "expected a maximum number of results"


def test_detailed_report_too_high_max_results():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "insightPlaybackLocationType": "EMBEDDED",
        "country": "US",
        "video": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    with pytest.raises(InvalidRequest) as exc:
        report.validate(d, f, m, s, 100)
    assert str(exc.value) == "expected no more than 25 results, got 100"


def test_detailed_report_start_index_too_high():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "insightPlaybackLocationType": "EMBEDDED",
        "country": "US",
        "video": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    with pytest.raises(InvalidRequest) as exc:
        report.validate(d, f, m, s, 25, 20)
    assert str(exc.value) == "the start index is too high"


def test_detailed_report_no_sort_options():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "insightPlaybackLocationType": "EMBEDDED",
        "country": "US",
        "video": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    with pytest.raises(InvalidRequest) as exc:
        report.validate(d, f, m, [], 25)
    assert str(exc.value) == "expected at least 1 sort option, got 0"
