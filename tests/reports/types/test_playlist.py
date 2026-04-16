# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import random

import pytest

from analytix.abc import ReportType
from analytix.errors import InvalidRequest
from analytix.reports.constants import VALID_FILTER_OPTIONS
from analytix.reports.types.playlist import BasicUserActivityPlaylist
from analytix.reports.types.playlist import DeviceTypeAndOperatingSystemPlaylist
from analytix.reports.types.playlist import DeviceTypePlaylist
from analytix.reports.types.playlist import GeographyBasedActivityPlaylist
from analytix.reports.types.playlist import GeographyBasedActivityUSPlaylist
from analytix.reports.types.playlist import OperatingSystemPlaylist
from analytix.reports.types.playlist import PlaybackLocationDetailPlaylist
from analytix.reports.types.playlist import PlaybackLocationPlaylist
from analytix.reports.types.playlist import TimeBasedActivityPlaylist
from analytix.reports.types.playlist import TopPlaylists
from analytix.reports.types.playlist import TrafficSourceDetailPlaylist
from analytix.reports.types.playlist import TrafficSourcePlaylist
from analytix.reports.types.playlist import ViewerDemographicsPlaylist


def select_metrics(rtype: ReportType):
    metrics = list(rtype.metrics.values)
    sort_options = list(rtype.sort_options.values)

    perms = [metrics]
    for _ in range(min(2, len(sort_options))):
        n = random.randint(1, len(sort_options))
        perms.append(random.sample(sort_options, n))

    return perms


def select_sort_options(metrics, descending_only=False):
    if descending_only:
        return [(f"-{m[0]}",) for m in metrics[1:]]
    return [(m[0], f"-{m[0]}") for m in metrics[1:]]


@pytest.mark.parametrize("dimensions", [()])
@pytest.mark.parametrize("filters", [{"playlist": "a1"}, {"group": "b2"}])
@pytest.mark.parametrize("metrics", m := select_metrics(BasicUserActivityPlaylist()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_basic_user_activity_playlist(dimensions, filters, metrics, sort_options):
    report = BasicUserActivityPlaylist()
    assert report.name == "Basic user activity for playlists"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [("day",), ("month",)])
@pytest.mark.parametrize("filters", [{"playlist": "a1"}, {"group": "b2"}])
@pytest.mark.parametrize("metrics", m := select_metrics(TimeBasedActivityPlaylist()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_time_based_activity_playlist(dimensions, filters, metrics, sort_options):
    report = TimeBasedActivityPlaylist()
    assert report.name == "Time-based activity for playlists"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [("country",)])
@pytest.mark.parametrize(
    "filters",
    [
        {"playlist": "a1"},
        {"group": "b2"},
        *[
            {"playlist": "a1", "continent": x}
            for x in VALID_FILTER_OPTIONS["continent"]
        ],
        *[{"group": "b2", "continent": x} for x in VALID_FILTER_OPTIONS["continent"]],
        *[
            {"playlist": "a1", "subContinent": x}
            for x in VALID_FILTER_OPTIONS["subContinent"]
        ],
        *[
            {"group": "b2", "subContinent": x}
            for x in VALID_FILTER_OPTIONS["subContinent"]
        ],
    ],
)
@pytest.mark.parametrize(
    "metrics",
    m := select_metrics(GeographyBasedActivityPlaylist()),
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_geography_based_activity_playlist(dimensions, filters, metrics, sort_options):
    report = GeographyBasedActivityPlaylist()
    assert report.name == "Geography-based activity for playlists"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [("country",)])
@pytest.mark.parametrize(
    "filters",
    [
        {"playlist": "a1", "continent": "015"},
        {"group": "b2", "continent": "015"},
        {"playlist": "a1", "subContinent": "002"},
        {"group": "b2", "subContinent": "002"},
    ],
)
@pytest.mark.parametrize(
    "metrics",
    m := select_metrics(GeographyBasedActivityPlaylist()),
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_geography_based_activity_playlist_errors(
    dimensions,
    filters,
    metrics,
    sort_options,
):
    report = GeographyBasedActivityPlaylist()
    assert report.name == "Geography-based activity for playlists"
    with pytest.raises(InvalidRequest):
        report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [("province",)])
@pytest.mark.parametrize(
    "filters",
    [{"country": "US", "playlist": "a1"}, {"country": "US", "group": "b2"}],
)
@pytest.mark.parametrize(
    "metrics",
    m := select_metrics(GeographyBasedActivityUSPlaylist()),
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_geography_based_activity_us_playlist(
    dimensions,
    filters,
    metrics,
    sort_options,
):
    report = GeographyBasedActivityUSPlaylist()
    assert report.name == "Geography-based activity for playlists (US)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [("insightPlaybackLocationType",)])
@pytest.mark.parametrize("filters", [{"playlist": "a1"}, {"group": "b2"}])
@pytest.mark.parametrize("metrics", m := select_metrics(PlaybackLocationPlaylist()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_playback_location_playlist(dimensions, filters, metrics, sort_options):
    report = PlaybackLocationPlaylist()
    assert report.name == "Playback locations for playlists"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [("insightPlaybackLocationDetail",)])
@pytest.mark.parametrize(
    "filters",
    [
        {"insightPlaybackLocationType": "EMBEDDED", "playlist": "a1"},
        {"insightPlaybackLocationType": "EMBEDDED", "group": "b2"},
    ],
)
@pytest.mark.parametrize(
    "metrics",
    m := select_metrics(PlaybackLocationDetailPlaylist()),
)
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_playback_location_detail_playlist(dimensions, filters, metrics, sort_options):
    report = PlaybackLocationDetailPlaylist()
    assert report.name == "Playback locations for playlists (detailed)"
    report.validate(dimensions, filters, metrics, sort_options, max_results=25)


@pytest.mark.parametrize("dimensions", [("insightTrafficSourceType",)])
@pytest.mark.parametrize("filters", [{"playlist": "a1"}, {"group": "b2"}])
@pytest.mark.parametrize("metrics", m := select_metrics(TrafficSourcePlaylist()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_traffic_source_playlist(dimensions, filters, metrics, sort_options):
    report = TrafficSourcePlaylist()
    assert report.name == "Traffic sources for playlists"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [("insightTrafficSourceDetail",)])
@pytest.mark.parametrize(
    "filters",
    [
        *[
            {"insightTrafficSourceType": x, "playlist": "a1"}
            for x in VALID_FILTER_OPTIONS["insightTrafficSourceDetail"]
        ],
        *[
            {"insightTrafficSourceType": x, "group": "b2"}
            for x in VALID_FILTER_OPTIONS["insightTrafficSourceDetail"]
        ],
    ],
)
@pytest.mark.parametrize(
    "metrics",
    m := select_metrics(TrafficSourceDetailPlaylist()),
)
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_traffic_source_detail_playlist(dimensions, filters, metrics, sort_options):
    report = TrafficSourceDetailPlaylist()
    assert report.name == "Traffic sources for playlists (detailed)"
    report.validate(dimensions, filters, metrics, sort_options, 25)


@pytest.mark.parametrize("dimensions", [("insightTrafficSourceDetail",)])
@pytest.mark.parametrize(
    "filters",
    [
        {"insightTrafficSourceType": "ANNOTATION", "playlist": "a1"},
        {"insightTrafficSourceType": "ANNOTATION", "group": "b2"},
        {"insightTrafficSourceType": "NO_LINK_EMBEDDED", "playlist": "a1"},
        {"insightTrafficSourceType": "NO_LINK_EMBEDDED", "group": "b2"},
        {"insightTrafficSourceType": "NO_LINK_OTHER", "playlist": "a1"},
        {"insightTrafficSourceType": "NO_LINK_OTHER", "group": "b2"},
        {"insightTrafficSourceType": "PLAYLIST", "playlist": "a1"},
        {"insightTrafficSourceType": "PLAYLIST", "group": "b2"},
        {"insightTrafficSourceType": "PROMOTED", "playlist": "a1"},
        {"insightTrafficSourceType": "PROMOTED", "group": "b2"},
        {"insightTrafficSourceType": "SHORTS", "playlist": "a1"},
        {"insightTrafficSourceType": "SHORTS", "group": "b2"},
        {"insightTrafficSourceType": "YT_PLAYLIST_PAGE", "playlist": "a1"},
        {"insightTrafficSourceType": "YT_PLAYLIST_PAGE", "group": "b2"},
    ],
)
@pytest.mark.parametrize(
    "metrics",
    m := select_metrics(TrafficSourceDetailPlaylist()),
)
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_traffic_source_detail_playlist_errors(
    dimensions,
    filters,
    metrics,
    sort_options,
):
    report = TrafficSourceDetailPlaylist()
    assert report.name == "Traffic sources for playlists (detailed)"
    with pytest.raises(InvalidRequest) as exc:
        report.validate(dimensions, filters, metrics, sort_options, 25)


@pytest.mark.parametrize("dimensions", [("deviceType",)])
@pytest.mark.parametrize("filters", [{"playlist": "a1"}, {"group": "b2"}])
@pytest.mark.parametrize("metrics", m := select_metrics(DeviceTypePlaylist()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_device_type_playlist(dimensions, filters, metrics, sort_options):
    report = DeviceTypePlaylist()
    assert report.name == "Device types for playlists"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [("operatingSystem",)])
@pytest.mark.parametrize("filters", [{"playlist": "a1"}, {"group": "b2"}])
@pytest.mark.parametrize("metrics", m := select_metrics(OperatingSystemPlaylist()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_operating_system_playlist(dimensions, filters, metrics, sort_options):
    report = OperatingSystemPlaylist()
    assert report.name == "Operating systems for playlists"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [("deviceType", "operatingSystem")])
@pytest.mark.parametrize("filters", [{"playlist": "a1"}, {"group": "b2"}])
@pytest.mark.parametrize(
    "metrics",
    m := select_metrics(DeviceTypeAndOperatingSystemPlaylist()),
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_device_type_and_operating_system_playlist(
    dimensions,
    filters,
    metrics,
    sort_options,
):
    report = DeviceTypeAndOperatingSystemPlaylist()
    assert report.name == "Device types and operating systems for playlists"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [("ageGroup",), ("gender",), ("ageGroup", "gender")],
)
@pytest.mark.parametrize("filters", [{"playlist": "a1"}, {"group": "b2"}])
@pytest.mark.parametrize(
    "metrics",
    m := select_metrics(ViewerDemographicsPlaylist()),
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_viewer_demographics_playlist(dimensions, filters, metrics, sort_options):
    report = ViewerDemographicsPlaylist()
    assert report.name == "Viewer demographics for playlists"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [("playlist",)])
@pytest.mark.parametrize("filters", [{}])
@pytest.mark.parametrize("metrics", m := select_metrics(TopPlaylists()))
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_top_playlists(dimensions, filters, metrics, sort_options):
    report = TopPlaylists()
    assert report.name == "Top playlists"
    report.validate(dimensions, filters, metrics, sort_options, 200)
