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

import random
import warnings
from typing import List
from typing import Set

import pytest

from analytix.abc import ReportType
from analytix.errors import InvalidRequest
from analytix.reports import data
from analytix.reports import types as rt


def select_metrics(rtype: ReportType):
    metrics = list(rtype.metrics.values)
    sort_options = list(rtype.sort_options.values)
    return [
        metrics,
        random.sample(sort_options, random.randint(1, len(sort_options))),
    ]


def select_sort_options(metrics, descending_only=False):
    if descending_only:
        return [(f"-{m[0]}",) for m in metrics[1:]]
    return [(m[0], f"-{m[0]}") for m in metrics[1:]]


def sample(s: Set[str], n: int = 3) -> List[str]:
    return s if len(s) < n else random.sample(list(s), n)


@pytest.mark.parametrize("dimensions", [()])
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.BasicUserActivity()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_basic_user_activity(dimensions, filters, metrics, sort_options):
    report = rt.BasicUserActivity()
    assert report.name == "Basic user activity"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [()])
@pytest.mark.parametrize(
    "filters",
    [
        {"country": "UK", "video": "rickroll"},
        {"country": "UK", "group": "rickroll"},
        {"continent": "015", "video": "rickroll"},
        {"continent": "015", "group": "rickroll"},
        {"subContinent": "002", "video": "rickroll"},
        {"subContinent": "002", "group": "rickroll"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.BasicUserActivity()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_basic_user_activity_errors(dimensions, filters, metrics, sort_options):
    report = rt.BasicUserActivity()
    assert report.name == "Basic user activity"
    with pytest.raises(InvalidRequest):
        report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [()])
@pytest.mark.parametrize(
    "filters",
    [
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        {"province": "US-OH", "video": "rickroll"},
        {"province": "US-OH", "group": "rickroll"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.BasicUserActivityUS()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_basic_user_activity_us(dimensions, filters, metrics, sort_options):
    report = rt.BasicUserActivityUS()
    assert report.name == "Basic user activity (US)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize("dimensions", [()])
@pytest.mark.parametrize(
    "filters",
    [
        {"province": "US-XX", "video": "rickroll"},
        {"province": "US-XX", "group": "rickroll"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.BasicUserActivityUS()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_basic_user_activity_us_errors(dimensions, filters, metrics, sort_options):
    report = rt.BasicUserActivityUS()
    assert report.name == "Basic user activity (US)"
    with pytest.raises(InvalidRequest):
        report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("day",),
        ("month",),
        ("day", "creatorContentType"),
        ("month", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.TimeBasedActivity()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_time_based_activity(dimensions, filters, metrics, sort_options):
    report = rt.TimeBasedActivity()
    assert report.name == "Time-based activity"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("day",),
        ("month",),
        ("day", "creatorContentType"),
        ("month", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        {"province": "US-OH", "video": "rickroll"},
        {"province": "US-OH", "group": "rickroll"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.TimeBasedActivityUS()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_time_based_activity_us(dimensions, filters, metrics, sort_options):
    report = rt.TimeBasedActivityUS()
    assert report.name == "Time-based activity (US)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [("country",), ("country", "creatorContentType")],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.GeographyBasedActivity()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_geography_based_activity(dimensions, filters, metrics, sort_options):
    report = rt.GeographyBasedActivity()
    assert report.name == "Geography-based activity"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [("province",), ("province", "creatorContentType")],
)
@pytest.mark.parametrize(
    "filters",
    [{"country": "US", "video": "rickroll"}, {"country": "US", "group": "rickroll"}],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.GeographyBasedActivityUS()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_geography_based_activity_us(dimensions, filters, metrics, sort_options):
    report = rt.GeographyBasedActivityUS()
    assert report.name == "Geography-based activity (US)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("city",),
        ("city", "creatorContentType"),
        ("city", "country"),
        ("city", "subscribedStatus"),
        ("city", "day"),
        ("city", "month"),
        (
            "city",
            "creatorContentType",
            "country",
            "subscribedStatus",
            "day",
        ),
        (
            "city",
            "creatorContentType",
            "country",
            "subscribedStatus",
            "month",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "province": "US-OH"},
        {"group": "rickroll", "province": "US-OH"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.GeographyBasedActivityByCity())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_geography_based_activity_by_city(dimensions, filters, metrics, sort_options):
    report = rt.GeographyBasedActivityByCity()
    assert report.name == "Geography-based activity (by city)"
    report.validate(dimensions, filters, metrics, sort_options, max_results=25)


def test_geography_based_activity_by_city_warning():
    report = rt.GeographyBasedActivityByCity()
    assert report.name == "Geography-based activity (by city)"
    d = ["city"]
    f = {}
    m = (
        "views",
        "estimatedMinutesWatched",
        "averageViewDuration",
        "averageViewPercentage",
    )
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]

    with warnings.catch_warnings(record=True) as warns:
        with pytest.raises(
            InvalidRequest, match="expected no more than 25 results, got 26"
        ):
            report.validate(d, f, m, s, 26)

        assert (
            "While the documentation says city reports can have a maximum of 250 results, the actual maximum the API accepts (currently) is 25"
            in str(warns[0].message)
        )


@pytest.mark.parametrize(
    "dimensions",
    [
        ("city",),
        ("city", "province"),
        ("city", "province", "day"),
        ("city", "province", "month"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {"country": "US"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.GeographyBasedActivityByCity())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_geography_based_activity_by_city_with_province(
    dimensions, filters, metrics, sort_options
):
    report = rt.GeographyBasedActivityByCity()
    assert report.name == "Geography-based activity (by city)"
    report.validate(dimensions, filters, metrics, sort_options, max_results=25)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("city", "province"),
        ("city", "province", "day"),
        ("city", "province", "month"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {"country": "UK"},
        {"continent": "002"},
        {"subContinent": "015"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.GeographyBasedActivityByCity())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_geography_based_activity_by_city_with_province_errors(
    dimensions, filters, metrics, sort_options
):
    report = rt.GeographyBasedActivityByCity()
    assert report.name == "Geography-based activity (by city)"
    with pytest.raises(InvalidRequest):
        report.validate(dimensions, filters, metrics, sort_options, max_results=25)


@pytest.mark.parametrize(
    "dimensions",
    [
        (),
        ("creatorContentType",),
        ("subscribedStatus",),
        ("day",),
        ("month",),
        ("creatorContentType", "day"),
        ("subscribedStatus", "day"),
        ("creatorContentType", "month"),
        ("subscribedStatus", "month"),
        ("creatorContentType", "subscribedStatus", "day"),
        ("creatorContentType", "subscribedStatus", "month"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "country": "US", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.PlaybackDetailsSubscribedStatus())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_playback_details_subscribed_status(dimensions, filters, metrics, sort_options):
    report = rt.PlaybackDetailsSubscribedStatus()
    assert report.name == "User activity by subscribed status"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        (),
        ("creatorContentType",),
        ("subscribedStatus",),
        ("day",),
        ("month",),
        ("creatorContentType", "day"),
        ("subscribedStatus", "day"),
        ("creatorContentType", "month"),
        ("subscribedStatus", "month"),
        ("creatorContentType", "subscribedStatus", "day"),
        ("creatorContentType", "subscribedStatus", "month"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "province": "US-OH"},
        {"group": "rickroll", "province": "US-OH"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "province": "US-OH", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.PlaybackDetailsSubscribedStatusUS())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_playback_details_subscribed_status_us(
    dimensions, filters, metrics, sort_options
):
    report = rt.PlaybackDetailsSubscribedStatusUS()
    assert report.name == "User activity by subscribed status (US)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        (),
        ("creatorContentType",),
        ("liveOrOnDemand",),
        ("subscribedStatus",),
        ("youtubeProduct",),
        ("day",),
        ("month",),
        ("creatorContentType", "day"),
        ("liveOrOnDemand", "day"),
        ("subscribedStatus", "day"),
        ("youtubeProduct", "day"),
        ("creatorContentType", "month"),
        ("liveOrOnDemand", "month"),
        ("subscribedStatus", "month"),
        ("youtubeProduct", "month"),
        (
            "creatorContentType",
            "liveOrOnDemand",
            "subscribedStatus",
            "youtubeProduct",
            "day",
        ),
        (
            "creatorContentType",
            "liveOrOnDemand",
            "subscribedStatus",
            "youtubeProduct",
            "month",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "province": "US-OH"},
        {"group": "rickroll", "province": "US-OH"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "liveOrOnDemand": "LIVE"},
        {"group": "rickroll", "liveOrOnDemand": "ON_DEMAND"},
        *[
            {"video": "rickroll", "youtubeProduct": x}
            for x in sample(data.VALID_FILTER_OPTIONS["youtubeProduct"])
        ],
        {"group": "rickroll", "youtubeProduct": "CORE"},
        {"video": "rickroll", "country": "US", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "province": "US-OH", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.PlaybackDetailsLiveTimeBased())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_playback_details_live_time_based(dimensions, filters, metrics, sort_options):
    report = rt.PlaybackDetailsLiveTimeBased()
    assert report.name == "Time-based playback details (live)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        (),
        ("creatorContentType",),
        ("subscribedStatus",),
        ("youtubeProduct",),
        ("day",),
        ("month",),
        ("creatorContentType", "day"),
        ("subscribedStatus", "day"),
        ("youtubeProduct", "day"),
        ("creatorContentType", "month"),
        ("subscribedStatus", "month"),
        ("youtubeProduct", "month"),
        (
            "creatorContentType",
            "subscribedStatus",
            "youtubeProduct",
            "day",
        ),
        (
            "creatorContentType",
            "subscribedStatus",
            "youtubeProduct",
            "month",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "province": "US-OH"},
        {"group": "rickroll", "province": "US-OH"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        *[
            {"video": "rickroll", "youtubeProduct": x}
            for x in sample(data.VALID_FILTER_OPTIONS["youtubeProduct"])
        ],
        {"video": "rickroll", "country": "US", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "province": "US-OH", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.PlaybackDetailsViewPercentageTimeBased())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_playback_details_view_percentage_time_based(
    dimensions, filters, metrics, sort_options
):
    report = rt.PlaybackDetailsViewPercentageTimeBased()
    assert report.name == "Time-based playback details (view percentage)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("country",),
        ("country", "creatorContentType"),
        ("country", "liveOrOnDemand"),
        ("country", "subscribedStatus"),
        ("country", "youtubeProduct"),
        (
            "country",
            "creatorContentType",
            "liveOrOnDemand",
            "subscribedStatus",
            "youtubeProduct",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "liveOrOnDemand": "LIVE"},
        {"group": "rickroll", "liveOrOnDemand": "ON_DEMAND"},
        *[
            {"video": "rickroll", "youtubeProduct": x}
            for x in sample(data.VALID_FILTER_OPTIONS["youtubeProduct"])
        ],
        {"group": "rickroll", "youtubeProduct": "CORE"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.PlaybackDetailsLiveGeographyBased())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_playback_details_live_geography_based(
    dimensions, filters, metrics, sort_options
):
    report = rt.PlaybackDetailsLiveGeographyBased()
    assert report.name == "Geography-based playback details (live)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("country",),
        ("country", "creatorContentType"),
        ("country", "subscribedStatus"),
        ("country", "youtubeProduct"),
        (
            "country",
            "creatorContentType",
            "subscribedStatus",
            "youtubeProduct",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        *[
            {"video": "rickroll", "youtubeProduct": x}
            for x in sample(data.VALID_FILTER_OPTIONS["youtubeProduct"])
        ],
        {"group": "rickroll", "youtubeProduct": "CORE"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.PlaybackDetailsViewPercentageGeographyBased())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_playback_details_view_percentage_geography_based(
    dimensions, filters, metrics, sort_options
):
    report = rt.PlaybackDetailsViewPercentageGeographyBased()
    assert report.name == "Geography-based playback details (view percentage)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("province",),
        ("province", "creatorContentType"),
        ("province", "liveOrOnDemand"),
        ("province", "subscribedStatus"),
        ("province", "youtubeProduct"),
        (
            "province",
            "creatorContentType",
            "liveOrOnDemand",
            "subscribedStatus",
            "youtubeProduct",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {"country": "US"},
        {"country": "US", "video": "rickroll"},
        {"country": "US", "group": "rickroll"},
        {"country": "US", "video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"country": "US", "group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"country": "US", "video": "rickroll", "liveOrOnDemand": "LIVE"},
        {"country": "US", "group": "rickroll", "liveOrOnDemand": "ON_DEMAND"},
        *[
            {"country": "US", "video": "rickroll", "youtubeProduct": x}
            for x in sample(data.VALID_FILTER_OPTIONS["youtubeProduct"])
        ],
        {"country": "US", "group": "rickroll", "youtubeProduct": "CORE"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.PlaybackDetailsLiveGeographyBasedUS())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_playback_details_live_geography_based_us(
    dimensions, filters, metrics, sort_options
):
    report = rt.PlaybackDetailsLiveGeographyBasedUS()
    assert report.name == "Geography-based playback details (live, US)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("province",),
        ("province", "creatorContentType"),
        ("province", "subscribedStatus"),
        ("province", "youtubeProduct"),
        (
            "province",
            "creatorContentType",
            "subscribedStatus",
            "youtubeProduct",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {"country": "US"},
        {"country": "US", "video": "rickroll"},
        {"country": "US", "group": "rickroll"},
        {"country": "US", "video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"country": "US", "group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        *[
            {"country": "US", "video": "rickroll", "youtubeProduct": x}
            for x in sample(data.VALID_FILTER_OPTIONS["youtubeProduct"])
        ],
        {"country": "US", "group": "rickroll", "youtubeProduct": "CORE"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.PlaybackDetailsViewPercentageGeographyBasedUS())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_playback_details_view_percentage_geography_based_us(
    dimensions, filters, metrics, sort_options
):
    report = rt.PlaybackDetailsViewPercentageGeographyBasedUS()
    assert report.name == "Geography-based playback details (view percentage, US)"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("insightPlaybackLocationType",),
        ("insightPlaybackLocationType", "creatorContentType"),
        ("insightPlaybackLocationType", "liveOrOnDemand"),
        ("insightPlaybackLocationType", "subscribedStatus"),
        ("insightPlaybackLocationType", "day"),
        (
            "insightPlaybackLocationType",
            "creatorContentType",
            "liveOrOnDemand",
            "subscribedStatus",
            "day",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "province": "US-OH"},
        {"group": "rickroll", "province": "US-OH"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "liveOrOnDemand": "LIVE"},
        {"group": "rickroll", "liveOrOnDemand": "ON_DEMAND"},
        {"video": "rickroll", "country": "US", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "province": "US-OH", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.PlaybackLocation()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_playback_location(dimensions, filters, metrics, sort_options):
    report = rt.PlaybackLocation()
    assert report.name == "Playback locations"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("insightPlaybackLocationDetail",),
        ("insightPlaybackLocationDetail", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {"insightPlaybackLocationType": "EMBEDDED"},
        *[
            {"insightPlaybackLocationType": "EMBEDDED", "country": x}
            for x in sample(data.COUNTRIES)
        ],
        *[
            {"insightPlaybackLocationType": "EMBEDDED", "province": x}
            for x in sample(data.SUBDIVISIONS)
        ],
        *[
            {"insightPlaybackLocationType": "EMBEDDED", "continent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["continent"])
        ],
        *[
            {"insightPlaybackLocationType": "EMBEDDED", "subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"insightPlaybackLocationType": "EMBEDDED", "video": "rickroll"},
        {"insightPlaybackLocationType": "EMBEDDED", "group": "rickroll"},
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "video": "rickroll",
            "country": "US",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "group": "rickroll",
            "country": "US",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "video": "rickroll",
            "province": "US-OH",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "group": "rickroll",
            "province": "US-OH",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "video": "rickroll",
            "continent": "002",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "group": "rickroll",
            "continent": "002",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "video": "rickroll",
            "subContinent": "015",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "group": "rickroll",
            "subContinent": "015",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "video": "rickroll",
            "subscribedStatus": "SUBSCRIBED",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "group": "rickroll",
            "subscribedStatus": "UNSUBSCRIBED",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "video": "rickroll",
            "liveOrOnDemand": "LIVE",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "group": "rickroll",
            "liveOrOnDemand": "ON_DEMAND",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "video": "rickroll",
            "country": "US",
            "subscribedStatus": "SUBSCRIBED",
        },
        {
            "insightPlaybackLocationType": "EMBEDDED",
            "video": "rickroll",
            "province": "US-OH",
            "subscribedStatus": "SUBSCRIBED",
        },
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.PlaybackLocationDetail()))
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_playback_location_detail(dimensions, filters, metrics, sort_options):
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    report.validate(dimensions, filters, metrics, sort_options, max_results=25)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("insightTrafficSourceType",),
        ("insightTrafficSourceType", "creatorContentType"),
        ("insightTrafficSourceType", "liveOrOnDemand"),
        ("insightTrafficSourceType", "subscribedStatus"),
        ("insightTrafficSourceType", "day"),
        (
            "insightTrafficSourceType",
            "creatorContentType",
            "liveOrOnDemand",
            "subscribedStatus",
            "day",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "province": "US-OH"},
        {"group": "rickroll", "province": "US-OH"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "liveOrOnDemand": "LIVE"},
        {"group": "rickroll", "liveOrOnDemand": "ON_DEMAND"},
        {"video": "rickroll", "country": "US", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "province": "US-OH", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.TrafficSource()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_traffic_source(dimensions, filters, metrics, sort_options):
    report = rt.TrafficSource()
    assert report.name == "Traffic sources"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("insightTrafficSourceDetail",),
        ("insightTrafficSourceDetail", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        *[
            {"insightTrafficSourceType": x}
            for x in data.VALID_FILTER_OPTIONS["insightTrafficSourceDetail"]
        ],
        *[
            {"insightTrafficSourceType": "ADVERTISING", "country": x}
            for x in sample(data.COUNTRIES)
        ],
        *[
            {"insightTrafficSourceType": "ADVERTISING", "province": x}
            for x in sample(data.SUBDIVISIONS)
        ],
        *[
            {"insightTrafficSourceType": "ADVERTISING", "continent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["continent"])
        ],
        *[
            {"insightTrafficSourceType": "ADVERTISING", "subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"insightTrafficSourceType": "ADVERTISING", "video": "rickroll"},
        {"insightTrafficSourceType": "ADVERTISING", "group": "rickroll"},
        {
            "insightTrafficSourceType": "ADVERTISING",
            "video": "rickroll",
            "country": "US",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "group": "rickroll",
            "country": "US",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "video": "rickroll",
            "province": "US-OH",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "group": "rickroll",
            "province": "US-OH",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "video": "rickroll",
            "continent": "002",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "group": "rickroll",
            "continent": "002",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "video": "rickroll",
            "subContinent": "015",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "group": "rickroll",
            "subContinent": "015",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "video": "rickroll",
            "subscribedStatus": "SUBSCRIBED",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "group": "rickroll",
            "subscribedStatus": "UNSUBSCRIBED",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "video": "rickroll",
            "liveOrOnDemand": "LIVE",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "group": "rickroll",
            "liveOrOnDemand": "ON_DEMAND",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "video": "rickroll",
            "country": "US",
            "subscribedStatus": "SUBSCRIBED",
        },
        {
            "insightTrafficSourceType": "ADVERTISING",
            "video": "rickroll",
            "province": "US-OH",
            "subscribedStatus": "SUBSCRIBED",
        },
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.TrafficSourceDetail()))
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_traffic_source_detail(dimensions, filters, metrics, sort_options):
    report = rt.TrafficSourceDetail()
    assert report.name == "Traffic sources (detailed)"
    report.validate(dimensions, filters, metrics, sort_options, max_results=25)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("insightTrafficSourceDetail",),
        ("insightTrafficSourceDetail", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        *[
            {"insightTrafficSourceType": x}
            for x in set(data.VALID_FILTER_OPTIONS["insightTrafficSourceType"])
            - set(data.VALID_FILTER_OPTIONS["insightTrafficSourceDetail"])
        ],
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.TrafficSourceDetail()))
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_traffic_source_detail_errors(dimensions, filters, metrics, sort_options):
    report = rt.TrafficSourceDetail()
    assert report.name == "Traffic sources (detailed)"
    with pytest.raises(InvalidRequest):
        report.validate(dimensions, filters, metrics, sort_options, max_results=25)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("deviceType",),
        ("deviceType", "creatorContentType"),
        ("deviceType", "day"),
        ("deviceType", "liveOrOnDemand"),
        ("deviceType", "subscribedStatus"),
        ("deviceType", "youtubeProduct"),
        (
            "deviceType",
            "creatorContentType",
            "day",
            "liveOrOnDemand",
            "subscribedStatus",
            "youtubeProduct",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "province": "US-OH"},
        {"group": "rickroll", "province": "US-OH"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "liveOrOnDemand": "LIVE"},
        {"group": "rickroll", "liveOrOnDemand": "ON_DEMAND"},
        {"video": "rickroll", "operatingSystem": "WINDOWS"},
        {"group": "rickroll", "operatingSystem": "MACINTOSH"},
        {"video": "rickroll", "youtubeProduct": "CORE"},
        {"group": "rickroll", "youtubeProduct": "GAMING"},
        {"video": "rickroll", "country": "US", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "province": "US-OH", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.DeviceType()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_device_type(dimensions, filters, metrics, sort_options):
    report = rt.DeviceType()
    assert report.name == "Device types"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("operatingSystem",),
        ("operatingSystem", "creatorContentType"),
        ("operatingSystem", "day"),
        ("operatingSystem", "liveOrOnDemand"),
        ("operatingSystem", "subscribedStatus"),
        ("operatingSystem", "youtubeProduct"),
        (
            "operatingSystem",
            "creatorContentType",
            "day",
            "liveOrOnDemand",
            "subscribedStatus",
            "youtubeProduct",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "province": "US-OH"},
        {"group": "rickroll", "province": "US-OH"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "liveOrOnDemand": "LIVE"},
        {"group": "rickroll", "liveOrOnDemand": "ON_DEMAND"},
        {"video": "rickroll", "deviceType": "DESKTOP"},
        {"group": "rickroll", "deviceType": "MOBILE"},
        {"video": "rickroll", "youtubeProduct": "CORE"},
        {"group": "rickroll", "youtubeProduct": "GAMING"},
        {"video": "rickroll", "country": "US", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "province": "US-OH", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.OperatingSystem()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_operating_system(dimensions, filters, metrics, sort_options):
    report = rt.OperatingSystem()
    assert report.name == "Operating systems"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("deviceType", "operatingSystem"),
        ("deviceType", "operatingSystem", "creatorContentType"),
        ("deviceType", "operatingSystem", "day"),
        ("deviceType", "operatingSystem", "liveOrOnDemand"),
        ("deviceType", "operatingSystem", "subscribedStatus"),
        ("deviceType", "operatingSystem", "youtubeProduct"),
        (
            "deviceType",
            "operatingSystem",
            "creatorContentType",
            "day",
            "liveOrOnDemand",
            "subscribedStatus",
            "youtubeProduct",
        ),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "province": "US-OH"},
        {"group": "rickroll", "province": "US-OH"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "liveOrOnDemand": "LIVE"},
        {"group": "rickroll", "liveOrOnDemand": "ON_DEMAND"},
        {"video": "rickroll", "youtubeProduct": "CORE"},
        {"group": "rickroll", "youtubeProduct": "GAMING"},
        {"video": "rickroll", "country": "US", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "province": "US-OH", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.DeviceTypeAndOperatingSystem())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_device_type_and_operating_system(dimensions, filters, metrics, sort_options):
    report = rt.DeviceTypeAndOperatingSystem()
    assert report.name == "Device types and operating systems"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("ageGroup",),
        ("gender",),
        ("ageGroup", "creatorContentType"),
        ("gender", "liveOrOnDemand"),
        ("ageGroup", "subscribedStatus"),
        ("gender", "creatorContentType", "liveOrOnDemand", "subscribedStatus"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "province": "US-OH"},
        {"group": "rickroll", "province": "US-OH"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "liveOrOnDemand": "LIVE"},
        {"group": "rickroll", "liveOrOnDemand": "ON_DEMAND"},
        {"video": "rickroll", "country": "US", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "province": "US-OH", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.ViewerDemographics()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_viewer_demographics(dimensions, filters, metrics, sort_options):
    report = rt.ViewerDemographics()
    assert report.name == "Viewer demographics"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("sharingService",),
        ("sharingService", "creatorContentType"),
        ("sharingService", "subscribedStatus"),
        ("sharingService", "creatorContentType", "subscribedStatus"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
        {"video": "rickroll"},
        {"group": "rickroll"},
        {"video": "rickroll", "country": "US"},
        {"group": "rickroll", "country": "US"},
        {"video": "rickroll", "continent": "002"},
        {"group": "rickroll", "continent": "002"},
        {"video": "rickroll", "subContinent": "015"},
        {"group": "rickroll", "subContinent": "015"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"group": "rickroll", "subscribedStatus": "UNSUBSCRIBED"},
        {"video": "rickroll", "country": "US", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize(
    "metrics", m := select_metrics(rt.EngagementAndContentSharing())
)
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_engagement_and_content_sharing(dimensions, filters, metrics, sort_options):
    report = rt.EngagementAndContentSharing()
    assert report.name == "Engagement and content sharing"
    report.validate(dimensions, filters, metrics, sort_options)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("elapsedVideoTimeRatio",),
        ("elapsedVideoTimeRatio", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {"video": "rickroll"},
        {"video": "rickroll", "audienceType": "ORGANIC"},
        {"video": "rickroll", "subscribedStatus": "SUBSCRIBED"},
        {"video": "rickroll", "youtubeProduct": "CORE"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.AudienceRetention()))
@pytest.mark.parametrize("sort_options", select_sort_options(m))
def test_audience_retention(dimensions, filters, metrics, sort_options):
    report = rt.AudienceRetention()
    assert report.name == "Audience retention"
    report.validate(dimensions, filters, metrics, sort_options)


def test_audience_retention_invalid_video_filters():
    report = rt.AudienceRetention()
    assert report.name == "Audience retention"
    d = ["elapsedVideoTimeRatio"]
    f = {"video": "fn849bng984b,f327b98g3b8g"}
    m = ["audienceWatchRatio", "relativeRetentionPerformance"]
    s = ["audienceWatchRatio", "relativeRetentionPerformance"]
    with pytest.raises(
        InvalidRequest,
        match="only one video ID can be provided when 'elapsedVideoTimeRatio' is a dimension",
    ):
        report.validate(d, f, m, s)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("video",),
        ("video", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        *[{"country": x} for x in sample(data.COUNTRIES)],
        *[{"continent": x} for x in sample(data.VALID_FILTER_OPTIONS["continent"])],
        *[
            {"subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.TopVideosRegional()))
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_top_videos_regional(dimensions, filters, metrics, sort_options):
    report = rt.TopVideosRegional()
    assert report.name == "Top videos by region"
    report.validate(dimensions, filters, metrics, sort_options, max_results=200)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("video",),
        ("video", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        *[{"province": x} for x in sample(data.SUBDIVISIONS)],
        {"province": "US-OH", "subscribedStatus": "SUBSCRIBED"},
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.TopVideosUS()))
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_top_videos_us(dimensions, filters, metrics, sort_options):
    report = rt.TopVideosUS()
    assert report.name == "Top videos by state"
    report.validate(dimensions, filters, metrics, sort_options, max_results=200)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("video",),
        ("video", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        {"subscribedStatus": "SUBSCRIBED"},
        *[
            {"subscribedStatus": "SUBSCRIBED", "country": x}
            for x in sample(data.COUNTRIES)
        ],
        *[
            {"subscribedStatus": "SUBSCRIBED", "continent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["continent"])
        ],
        *[
            {"subscribedStatus": "SUBSCRIBED", "subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.TopVideosSubscribed()))
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_top_videos_subscribed(dimensions, filters, metrics, sort_options):
    report = rt.TopVideosSubscribed()
    assert report.name == "Top videos by subscription status"
    report.validate(dimensions, filters, metrics, sort_options, max_results=200)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("video",),
        ("video", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        {"youtubeProduct": "CORE"},
        {"subscribedStatus": "SUBSCRIBED"},
        *[{"youtubeProduct": "CORE", "country": x} for x in sample(data.COUNTRIES)],
        *[{"youtubeProduct": "CORE", "province": x} for x in sample(data.SUBDIVISIONS)],
        *[
            {"youtubeProduct": "CORE", "continent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["continent"])
        ],
        *[
            {"youtubeProduct": "CORE", "subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.TopVideosYouTubeProduct()))
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_top_videos_youtube_product(dimensions, filters, metrics, sort_options):
    report = rt.TopVideosYouTubeProduct()
    assert report.name == "Top videos by YouTube product"
    report.validate(dimensions, filters, metrics, sort_options, max_results=200)


@pytest.mark.parametrize(
    "dimensions",
    [
        ("video",),
        ("video", "creatorContentType"),
    ],
)
@pytest.mark.parametrize(
    "filters",
    [
        {},
        {"liveOrOnDemand": "LIVE"},
        {"youtubeProduct": "CORE"},
        {"subscribedStatus": "SUBSCRIBED"},
        *[{"liveOrOnDemand": "LIVE", "country": x} for x in sample(data.COUNTRIES)],
        *[{"liveOrOnDemand": "LIVE", "province": x} for x in sample(data.SUBDIVISIONS)],
        *[
            {"liveOrOnDemand": "LIVE", "continent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["continent"])
        ],
        *[
            {"liveOrOnDemand": "LIVE", "subContinent": x}
            for x in sample(data.VALID_FILTER_OPTIONS["subContinent"])
        ],
    ],
)
@pytest.mark.parametrize("metrics", m := select_metrics(rt.TopVideosPlaybackDetail()))
@pytest.mark.parametrize("sort_options", select_sort_options(m, descending_only=True))
def test_top_videos_playback_detail(dimensions, filters, metrics, sort_options):
    report = rt.TopVideosPlaybackDetail()
    assert report.name == "Top videos by playback detail"
    report.validate(dimensions, filters, metrics, sort_options, max_results=200)
