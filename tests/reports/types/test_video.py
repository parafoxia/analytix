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
from analytix.reports import data
from analytix.reports import types as rt
from analytix.reports.features import Filters, Required, ZeroOrOne

# BASIC USER ACTIVITY


def test_basic_user_activity_1():
    report = rt.BasicUserActivity()
    assert report.name == "Basic user activity"
    d = []
    f = {"country": "US", "video": "nf97ng98bg9"}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


def test_basic_user_activity_2():
    report = rt.BasicUserActivity()
    assert report.name == "Basic user activity"
    d = []
    f = {"continent": "002", "group": "fn849bng984b"}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


def test_basic_user_activity_3():
    report = rt.BasicUserActivity()
    assert report.name == "Basic user activity"
    d = []
    f = {"subContinent": "014"}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


def test_basic_user_activity_4():
    report = rt.BasicUserActivity()
    assert report.name == "Basic user activity"
    d = []
    f = {}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


# BASIC USER ACTIVITY (US)


def test_basic_user_activity_us_1():
    report = rt.BasicUserActivityUS()
    assert report.name == "Basic user activity (US)"
    d = []
    f = {"province": "US-OH", "video": "fnu74ng98wb49g"}
    m = data.ALL_PROVINCE_METRICS
    s = data.ALL_PROVINCE_METRICS
    report.validate(d, f, m, s)


def test_basic_user_activity_us_2():
    report = rt.BasicUserActivityUS()
    assert report.name == "Basic user activity (US)"
    d = []
    f = {"province": "US-OH", "group": "fnu74ng98wb49g"}
    m = data.ALL_PROVINCE_METRICS
    s = data.ALL_PROVINCE_METRICS
    report.validate(d, f, m, s)


def test_basic_user_activity_us_3():
    report = rt.BasicUserActivityUS()
    assert report.name == "Basic user activity (US)"
    d = []
    f = {"province": "US-OH"}
    m = data.ALL_PROVINCE_METRICS
    s = data.ALL_PROVINCE_METRICS
    report.validate(d, f, m, s)


# TIME-BASED ACTIVITY


def test_time_based_activity_1():
    report = rt.TimeBasedActivity()
    assert report.name == "Time-based activity"
    d = ["day"]
    f = {"country": "US", "video": "nf97ng98bg9"}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


def test_time_based_activity_2():
    report = rt.TimeBasedActivity()
    assert report.name == "Time-based activity"
    d = ["month"]
    f = {"continent": "002", "group": "fn849bng984b"}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


def test_time_based_activity_3():
    report = rt.TimeBasedActivity()
    assert report.name == "Time-based activity"
    d = ["day"]
    f = {"subContinent": "014"}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


def test_time_based_activity_4():
    report = rt.TimeBasedActivity()
    assert report.name == "Time-based activity"
    d = ["month"]
    f = {}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


# TIME-BASED ACTIVITY (US)


def test_time_based_activity_us_1():
    report = rt.TimeBasedActivityUS()
    assert report.name == "Time-based activity (US)"
    d = ["day"]
    f = {"province": "US-OH", "video": "fnu74ng98wb49g"}
    m = data.ALL_PROVINCE_METRICS
    s = data.ALL_PROVINCE_METRICS
    report.validate(d, f, m, s)


def test_time_based_activity_us_2():
    report = rt.TimeBasedActivityUS()
    assert report.name == "Time-based activity (US)"
    d = ["month"]
    f = {"province": "US-OH", "group": "fnu74ng98wb49g"}
    m = data.ALL_PROVINCE_METRICS
    s = data.ALL_PROVINCE_METRICS
    report.validate(d, f, m, s)


def test_time_based_activity_us_3():
    report = rt.TimeBasedActivityUS()
    assert report.name == "Time-based activity (US)"
    d = ["day"]
    f = {"province": "US-OH"}
    m = data.ALL_PROVINCE_METRICS
    s = data.ALL_PROVINCE_METRICS
    report.validate(d, f, m, s)


# GEOGRAPHY-BASED ACTIVITY


def test_geography_based_activity_1():
    report = rt.GeographyBasedActivity()
    assert report.name == "Geography-based activity"
    d = ["country"]
    f = {"continent": "002", "video": "fn849bng984b"}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


def test_geography_based_activity_2():
    report = rt.GeographyBasedActivity()
    assert report.name == "Geography-based activity"
    d = ["country"]
    f = {"subContinent": "014", "group": "fn849bng984b"}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


def test_geography_based_activity_3():
    report = rt.GeographyBasedActivity()
    assert report.name == "Geography-based activity"
    d = ["country"]
    f = {}
    m = data.ALL_VIDEO_METRICS
    s = data.ALL_VIDEO_METRICS
    report.validate(d, f, m, s)


# GEOGRAPHY-BASED ACTIVITY (US)


def test_geography_based_activity_us_1():
    report = rt.GeographyBasedActivityUS()
    assert report.name == "Geography-based activity (US)"
    d = ["province"]
    f = {"country": "US", "video": "fn849bng984b"}
    m = data.ALL_PROVINCE_METRICS
    s = data.ALL_PROVINCE_METRICS
    report.validate(d, f, m, s)


def test_geography_based_activity_us_2():
    report = rt.GeographyBasedActivityUS()
    assert report.name == "Geography-based activity (US)"
    d = ["province"]
    f = {"country": "US", "group": "fn849bng984b"}
    m = data.ALL_PROVINCE_METRICS
    s = data.ALL_PROVINCE_METRICS
    report.validate(d, f, m, s)


def test_geography_based_activity_us_3():
    report = rt.GeographyBasedActivityUS()
    assert report.name == "Geography-based activity (US)"
    d = ["province"]
    f = {"country": "US"}
    m = data.ALL_PROVINCE_METRICS
    s = data.ALL_PROVINCE_METRICS
    report.validate(d, f, m, s)


# GEOGRAPHY-BASED ACTIVITY (BY CITY)


def test_geography_based_activity_by_city_1():
    report = rt.GeographyBasedActivityByCity()
    assert report.name == "Geography-based activity (by city)"
    d = ["city", "creatorContentType", "day"]
    f = {"country": "US", "video": "fn849bng984b"}
    m = (
        "views",
        "estimatedMinutesWatched",
        "averageViewDuration",
        "averageViewPercentage",
    )
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_geography_based_activity_by_city_2():
    report = rt.GeographyBasedActivityByCity()
    assert report.name == "Geography-based activity (by city)"
    d = ["city", "country", "month"]
    f = {"province": "US-OH", "group": "fn849bng984b"}
    m = (
        "views",
        "estimatedMinutesWatched",
        "averageViewDuration",
        "averageViewPercentage",
    )
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_geography_based_activity_by_city_3():
    report = rt.GeographyBasedActivityByCity()
    assert report.name == "Geography-based activity (by city)"
    d = ["city", "province"]
    f = {"country": "US"}
    m = (
        "views",
        "estimatedMinutesWatched",
        "averageViewDuration",
        "averageViewPercentage",
    )
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)

    assert report.filters == Filters(
        Required("country==US"), ZeroOrOne("video", "group")
    )


def test_geography_based_activity_by_city_4():
    report = rt.GeographyBasedActivityByCity()
    assert report.name == "Geography-based activity (by city)"
    d = ["city", "subscribedStatus"]
    f = {"continent": "002"}
    m = (
        "views",
        "estimatedMinutesWatched",
        "averageViewDuration",
        "averageViewPercentage",
    )
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_geography_based_activity_by_city_5():
    report = rt.GeographyBasedActivityByCity()
    assert report.name == "Geography-based activity (by city)"
    d = ["city"]
    f = {"subContinent": "014"}
    m = (
        "views",
        "estimatedMinutesWatched",
        "averageViewDuration",
        "averageViewPercentage",
    )
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_geography_based_activity_by_city_6():
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
    report.validate(d, f, m, s, 25)


def test_geography_based_activity_by_city_7(caplog):
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

    with pytest.raises(
        InvalidRequest, match="expected no more than 25 results, got 26"
    ):
        report.validate(d, f, m, s, 26)

    assert (
        "While the documentation says city reports can have a maximum of 250 results, the actual maxiumum the API accepts (currently) is 25"
        in caplog.text
    )


# PLAYBACK DETAILS: SUBSCRIBED STATUS


def test_playback_details_subscribed_status_1():
    report = rt.PlaybackDetailsSubscribedStatus()
    assert report.name == "User activity by subscribed status"
    d = ["subscribedStatus", "day"]
    f = {"country": "US", "video": "fn849bng984b"}
    m = data.SUBSCRIPTION_METRICS
    s = data.SUBSCRIPTION_METRICS
    report.validate(d, f, m, s)


def test_playback_details_subscribed_status_2():
    report = rt.PlaybackDetailsSubscribedStatus()
    assert report.name == "User activity by subscribed status"
    d = ["month"]
    f = {"continent": "002", "group": "fn849bng984b", "subscribedStatus": "SUBSCRIBED"}
    m = data.SUBSCRIPTION_METRICS
    s = data.SUBSCRIPTION_METRICS
    report.validate(d, f, m, s)


def test_playback_details_subscribed_status_3():
    report = rt.PlaybackDetailsSubscribedStatus()
    assert report.name == "User activity by subscribed status"
    d = []
    f = {"subContinent": "014"}
    m = data.SUBSCRIPTION_METRICS
    s = data.SUBSCRIPTION_METRICS
    report.validate(d, f, m, s)


def test_playback_details_subscribed_status_4():
    report = rt.PlaybackDetailsSubscribedStatus()
    assert report.name == "User activity by subscribed status"
    d = []
    f = {}
    m = data.SUBSCRIPTION_METRICS
    s = data.SUBSCRIPTION_METRICS
    report.validate(d, f, m, s)


# PLAYBACK DETAILS: SUBSCRIBED STATUS (US)


def test_playback_details_subscribed_status_us_1():
    report = rt.PlaybackDetailsSubscribedStatusUS()
    assert report.name == "User activity by subscribed status (US)"
    d = ["subscribedStatus", "day"]
    f = {"video": "fn849bng984b", "province": "US-OH"}
    m = data.LESSER_SUBSCRIPTION_METRICS
    s = data.LESSER_SUBSCRIPTION_METRICS
    report.validate(d, f, m, s)


def test_playback_details_subscribed_status_us_2():
    report = rt.PlaybackDetailsSubscribedStatusUS()
    assert report.name == "User activity by subscribed status (US)"
    d = ["month"]
    f = {"group": "fn849bng984b", "province": "US-OH", "subscribedStatus": "SUBSCRIBED"}
    m = data.LESSER_SUBSCRIPTION_METRICS
    s = data.LESSER_SUBSCRIPTION_METRICS
    report.validate(d, f, m, s)


def test_playback_details_subscribed_status_us_3():
    report = rt.PlaybackDetailsSubscribedStatusUS()
    assert report.name == "User activity by subscribed status (US)"
    d = []
    f = {}
    m = data.LESSER_SUBSCRIPTION_METRICS
    s = data.LESSER_SUBSCRIPTION_METRICS
    report.validate(d, f, m, s)


# PLAYBACK DETAILS: TIME-BASED (LIVE)


def test_playback_details_live_time_based_1():
    report = rt.PlaybackDetailsLiveTimeBased()
    assert report.name == "Time-based playback details (live)"
    d = ["subscribedStatus", "day"]
    f = {"country": "US", "video": "fn849bng984b", "youtubeProduct": "CORE"}
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_live_time_based_2():
    report = rt.PlaybackDetailsLiveTimeBased()
    assert report.name == "Time-based playback details (live)"
    d = ["subscribedStatus", "liveOrOnDemand", "month"]
    f = {
        "continent": "002",
        "group": "fn849bng984b",
        "youtubeProduct": "CORE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_live_time_based_3():
    report = rt.PlaybackDetailsLiveTimeBased()
    assert report.name == "Time-based playback details (live)"
    d = ["subscribedStatus", "liveOrOnDemand", "youtubeProduct"]
    f = {
        "subContinent": "014",
        "youtubeProduct": "CORE",
        "subscribedStatus": "SUBSCRIBED",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_live_time_based_4():
    report = rt.PlaybackDetailsLiveTimeBased()
    assert report.name == "Time-based playback details (live)"
    d = []
    f = {"province": "US-OH"}
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_live_time_based_5():
    report = rt.PlaybackDetailsLiveTimeBased()
    assert report.name == "Time-based playback details (live)"
    d = []
    f = {}
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


# PLAYBACK DETAILS: TIME-BASED (VIEW PERCENTAGE)


def test_playback_details_view_percentage_time_based_1():
    report = rt.PlaybackDetailsViewPercentageTimeBased()
    assert report.name == "Time-based playback details (view percentage)"
    d = ["subscribedStatus", "day"]
    f = {"country": "US", "video": "fn849bng984b", "youtubeProduct": "CORE"}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_view_percentage_time_based_2():
    report = rt.PlaybackDetailsViewPercentageTimeBased()
    assert report.name == "Time-based playback details (view percentage)"
    d = ["subscribedStatus", "youtubeProduct", "month"]
    f = {
        "continent": "002",
        "group": "fn849bng984b",
        "youtubeProduct": "CORE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_view_percentage_time_based_3():
    report = rt.PlaybackDetailsViewPercentageTimeBased()
    assert report.name == "Time-based playback details (view percentage)"
    d = []
    f = {"province": "US-OH"}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_view_percentage_time_based_4():
    report = rt.PlaybackDetailsViewPercentageTimeBased()
    assert report.name == "Time-based playback details (view percentage)"
    d = []
    f = {}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


# PLAYBACK DETAILS: GEOGRAPHY-BASED (LIVE)


def test_playback_details_live_geography_based_1():
    report = rt.PlaybackDetailsLiveGeographyBased()
    assert report.name == "Geography-based playback details (live)"
    d = ["country", "liveOrOnDemand"]
    f = {"continent": "002", "video": "fn849bng984b", "youtubeProduct": "CORE"}
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_live_geography_based_2():
    report = rt.PlaybackDetailsLiveGeographyBased()
    assert report.name == "Geography-based playback details (live)"
    d = ["country", "liveOrOnDemand", "subscribedStatus"]
    f = {
        "subContinent": "014",
        "group": "fn849bng984b",
        "youtubeProduct": "CORE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_live_geography_based_3():
    report = rt.PlaybackDetailsLiveGeographyBased()
    assert report.name == "Geography-based playback details (live)"
    d = ["country", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"]
    f = {
        "youtubeProduct": "CORE",
        "subscribedStatus": "SUBSCRIBED",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_live_geography_based_4():
    report = rt.PlaybackDetailsLiveGeographyBased()
    assert report.name == "Geography-based playback details (live)"
    d = ["country"]
    f = {}
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


# PLAYBACK DETAILS: GEOGRAPHY-BASED (VIEW PERCENTAGE)


def test_playback_details_view_percentage_geography_based_1():
    report = rt.PlaybackDetailsViewPercentageGeographyBased()
    assert report.name == "Geography-based playback details (view percentage)"
    d = ["country", "subscribedStatus"]
    f = {"continent": "002", "video": "fn849bng984b", "youtubeProduct": "CORE"}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_view_percentage_geography_based_2():
    report = rt.PlaybackDetailsViewPercentageGeographyBased()
    assert report.name == "Geography-based playback details (view percentage)"
    d = ["country", "subscribedStatus", "youtubeProduct"]
    f = {
        "subContinent": "014",
        "group": "fn849bng984b",
        "youtubeProduct": "CORE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_view_percentage_geography_based_3():
    report = rt.PlaybackDetailsViewPercentageGeographyBased()
    assert report.name == "Geography-based playback details (view percentage)"
    d = ["country"]
    f = {}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


# PLAYBACK DETAILS: GEOGRAPHY-BASED (LIVE, US)


def test_playback_details_live_geography_based_us_1():
    report = rt.PlaybackDetailsLiveGeographyBasedUS()
    assert report.name == "Geography-based playback details (live, US)"
    d = ["province", "liveOrOnDemand"]
    f = {"country": "US", "video": "fn849bng984b", "youtubeProduct": "CORE"}
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_live_geography_based_us_2():
    report = rt.PlaybackDetailsLiveGeographyBasedUS()
    assert report.name == "Geography-based playback details (live, US)"
    d = ["province", "liveOrOnDemand", "subscribedStatus"]
    f = {
        "country": "US",
        "group": "fn849bng984b",
        "youtubeProduct": "CORE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_live_geography_based_us_3():
    report = rt.PlaybackDetailsLiveGeographyBasedUS()
    assert report.name == "Geography-based playback details (live, US)"
    d = ["province", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"]
    f = {
        "country": "US",
        "youtubeProduct": "CORE",
        "subscribedStatus": "SUBSCRIBED",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_live_geography_based_us_4():
    report = rt.PlaybackDetailsLiveGeographyBasedUS()
    assert report.name == "Geography-based playback details (live, US)"
    d = ["province"]
    f = {"country": "US"}
    m = data.LIVE_PLAYBACK_DETAIL_METRICS
    s = data.LIVE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


# PLAYBACK DETAILS: GEOGRAPHY-BASED (VIEW PERCENTAGE, US)


def test_playback_details_view_percentage_geography_based_us_1():
    report = rt.PlaybackDetailsViewPercentageGeographyBasedUS()
    assert report.name == "Geography-based playback details (view percentage, US)"
    d = ["province", "subscribedStatus"]
    f = {"country": "US", "video": "fn849bng984b", "youtubeProduct": "CORE"}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_view_percentage_geography_based_us_2():
    report = rt.PlaybackDetailsViewPercentageGeographyBasedUS()
    assert report.name == "Geography-based playback details (view percentage, US)"
    d = ["province", "subscribedStatus", "youtubeProduct"]
    f = {
        "country": "US",
        "group": "fn849bng984b",
        "youtubeProduct": "CORE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


def test_playback_details_view_percentage_geography_based_us_3():
    report = rt.PlaybackDetailsViewPercentageGeographyBasedUS()
    assert report.name == "Geography-based playback details (view percentage, US)"
    d = ["province"]
    f = {"country": "US"}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    report.validate(d, f, m, s)


# PLAYBACK LOCATIONS


def test_playback_location_1():
    report = rt.PlaybackLocation()
    assert report.name == "Playback locations"
    d = ["insightPlaybackLocationType", "day"]
    f = {"country": "US", "video": "fn849bng984b", "liveOrOnDemand": "LIVE"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_playback_location_2():
    report = rt.PlaybackLocation()
    assert report.name == "Playback locations"
    d = ["insightPlaybackLocationType", "day", "liveOrOnDemand"]
    f = {
        "province": "US-OH",
        "group": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_playback_location_3():
    report = rt.PlaybackLocation()
    assert report.name == "Playback locations"
    d = ["insightPlaybackLocationType", "day", "liveOrOnDemand", "subscribedStatus"]
    f = {"continent": "002"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_playback_location_4():
    report = rt.PlaybackLocation()
    assert report.name == "Playback locations"
    d = ["insightPlaybackLocationType"]
    f = {"subContinent": "014"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_playback_location_5():
    report = rt.PlaybackLocation()
    assert report.name == "Playback locations"
    d = ["insightPlaybackLocationType"]
    f = {}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


# PLAYBACK LOCATIONS (DETAILED)


def test_playback_location_detail_1():
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
    report.validate(d, f, m, s, 25)


def test_playback_location_detail_2():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "insightPlaybackLocationType": "EMBEDDED",
        "province": "US-OH",
        "group": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_playback_location_detail_3():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {"insightPlaybackLocationType": "EMBEDDED", "continent": "002"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_playback_location_detail_4():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {"insightPlaybackLocationType": "EMBEDDED", "subContinent": "014"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_playback_location_detail_5():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {"insightPlaybackLocationType": "EMBEDDED"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


# TRAFFIC SOURCES


def test_traffic_source_1():
    report = rt.TrafficSource()
    assert report.name == "Traffic sources"
    d = ["insightTrafficSourceType", "day"]
    f = {"country": "US", "video": "fn849bng984b", "liveOrOnDemand": "LIVE"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_traffic_source_2():
    report = rt.TrafficSource()
    assert report.name == "Traffic sources"
    d = ["insightTrafficSourceType", "day", "liveOrOnDemand"]
    f = {
        "province": "US-OH",
        "group": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_traffic_source_3():
    report = rt.TrafficSource()
    assert report.name == "Traffic sources"
    d = ["insightTrafficSourceType", "day", "liveOrOnDemand", "subscribedStatus"]
    f = {"continent": "002"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_traffic_source_4():
    report = rt.TrafficSource()
    assert report.name == "Traffic sources"
    d = ["insightTrafficSourceType"]
    f = {"subContinent": "014"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_traffic_source_5():
    report = rt.TrafficSource()
    assert report.name == "Traffic sources"
    d = ["insightTrafficSourceType"]
    f = {}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


# TRAFFIC SOURCES (DETAILED)


def test_traffic_source_detail_1():
    report = rt.TrafficSourceDetail()
    assert report.name == "Traffic sources (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {
        "insightTrafficSourceType": "ADVERTISING",
        "country": "US",
        "video": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_traffic_source_detail_2():
    report = rt.TrafficSourceDetail()
    assert report.name == "Traffic sources (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {
        "insightTrafficSourceType": "ADVERTISING",
        "province": "US-OH",
        "group": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_traffic_source_detail_3():
    report = rt.TrafficSourceDetail()
    assert report.name == "Traffic sources (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {"insightTrafficSourceType": "ADVERTISING", "continent": "002"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_traffic_source_detail_4():
    report = rt.TrafficSourceDetail()
    assert report.name == "Traffic sources (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {"insightTrafficSourceType": "ADVERTISING", "subContinent": "014"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_traffic_source_detail_5():
    report = rt.TrafficSourceDetail()
    assert report.name == "Traffic sources (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {"insightTrafficSourceType": "ADVERTISING"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_traffic_source_detail_invalid_source():
    report = rt.TrafficSourceDetail()
    assert report.name == "Traffic sources (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {"insightTrafficSourceType": "ANNOTATION"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]

    with pytest.raises(
        InvalidRequest,
        match="dimensions and filters are incompatible with value 'ANNOTATION' for filter 'insightTrafficSourceType'",
    ):
        report.validate(d, f, m, s, 25)


# DEVICE TYPES


def test_device_type_1():
    report = rt.DeviceType()
    assert report.name == "Device types"
    d = ["deviceType", "day"]
    f = {"country": "US", "video": "fn849bng984b", "operatingSystem": "WINDOWS"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_device_type_2():
    report = rt.DeviceType()
    assert report.name == "Device types"
    d = ["deviceType", "day", "liveOrOnDemand", "subscribedStatus"]
    f = {
        "province": "US-OH",
        "group": "fn849bng984b",
        "operatingSystem": "WINDOWS",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_device_type_3():
    report = rt.DeviceType()
    assert report.name == "Device types"
    d = ["deviceType", "day", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"]
    f = {
        "continent": "002",
        "operatingSystem": "WINDOWS",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_device_type_4():
    report = rt.DeviceType()
    assert report.name == "Device types"
    d = ["deviceType"]
    f = {
        "subContinent": "014",
        "operatingSystem": "WINDOWS",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_device_type_5():
    report = rt.DeviceType()
    assert report.name == "Device types"
    d = ["deviceType"]
    f = {}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


# OPERATING SYSTEMS


def test_operating_system_1():
    report = rt.OperatingSystem()
    assert report.name == "Operating systems"
    d = ["operatingSystem", "day"]
    f = {"country": "US", "video": "fn849bng984b", "deviceType": "MOBILE"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_operating_system_2():
    report = rt.OperatingSystem()
    assert report.name == "Operating systems"
    d = ["operatingSystem", "day", "liveOrOnDemand", "subscribedStatus"]
    f = {
        "province": "US-OH",
        "group": "fn849bng984b",
        "deviceType": "MOBILE",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_operating_system_3():
    report = rt.OperatingSystem()
    assert report.name == "Operating systems"
    d = [
        "operatingSystem",
        "day",
        "liveOrOnDemand",
        "subscribedStatus",
        "youtubeProduct",
    ]
    f = {
        "continent": "002",
        "deviceType": "MOBILE",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_operating_system_4():
    report = rt.OperatingSystem()
    assert report.name == "Operating systems"
    d = ["operatingSystem"]
    f = {
        "subContinent": "014",
        "deviceType": "MOBILE",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_operating_system_5():
    report = rt.OperatingSystem()
    assert report.name == "Operating systems"
    d = ["operatingSystem"]
    f = {}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


# DEVICE TYPES AND OPERATING SYSTEMS


def test_device_type_and_operating_system_1():
    report = rt.DeviceTypeAndOperatingSystem()
    assert report.name == "Device types and operating systems"
    d = ["deviceType", "operatingSystem", "day"]
    f = {"country": "US", "video": "fn849bng984b"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_device_type_and_operating_system_2():
    report = rt.DeviceTypeAndOperatingSystem()
    assert report.name == "Device types and operating systems"
    d = ["deviceType", "operatingSystem", "day", "liveOrOnDemand", "subscribedStatus"]
    f = {
        "province": "US-OH",
        "group": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_device_type_and_operating_system_3():
    report = rt.DeviceTypeAndOperatingSystem()
    assert report.name == "Device types and operating systems"
    d = [
        "deviceType",
        "operatingSystem",
        "day",
        "liveOrOnDemand",
        "subscribedStatus",
        "youtubeProduct",
    ]
    f = {
        "continent": "002",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_device_type_and_operating_system_4():
    report = rt.DeviceTypeAndOperatingSystem()
    assert report.name == "Device types and operating systems"
    d = ["deviceType", "operatingSystem"]
    f = {
        "subContinent": "014",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


def test_device_type_and_operating_system_5():
    report = rt.DeviceTypeAndOperatingSystem()
    assert report.name == "Device types and operating systems"
    d = ["deviceType", "operatingSystem"]
    f = {}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = data.LOCATION_AND_TRAFFIC_METRICS
    report.validate(d, f, m, s)


# VIEWER DEMOGRAPHICS


def test_viewer_demographics_1():
    report = rt.ViewerDemographics()
    assert report.name == "Viewer demographics"
    d = ["ageGroup", "liveOrOnDemand"]
    f = {"country": "US", "video": "fn849bng984b", "liveOrOnDemand": "LIVE"}
    m = ["viewerPercentage"]
    s = ["viewerPercentage"]
    report.validate(d, f, m, s)


def test_viewer_demographics_2():
    report = rt.ViewerDemographics()
    assert report.name == "Viewer demographics"
    d = ["ageGroup", "gender", "liveOrOnDemand", "subscribedStatus"]
    f = {
        "province": "US-OH",
        "group": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = ["viewerPercentage"]
    s = ["viewerPercentage"]
    report.validate(d, f, m, s)


def test_viewer_demographics_3():
    report = rt.ViewerDemographics()
    assert report.name == "Viewer demographics"
    d = ["gender"]
    f = {"continent": "002"}
    m = ["viewerPercentage"]
    s = ["viewerPercentage"]
    report.validate(d, f, m, s)


def test_viewer_demographics_4():
    report = rt.ViewerDemographics()
    assert report.name == "Viewer demographics"
    d = ["ageGroup"]
    f = {"subContinent": "014"}
    m = ["viewerPercentage"]
    s = ["viewerPercentage"]
    report.validate(d, f, m, s)


def test_viewer_demographics_5():
    report = rt.ViewerDemographics()
    assert report.name == "Viewer demographics"
    d = ["ageGroup", "gender"]
    f = {}
    m = ["viewerPercentage"]
    s = ["viewerPercentage"]
    report.validate(d, f, m, s)


# ENGAGEMENT AND CONTENT SHARING


def test_engagement_and_content_sharing_1():
    report = rt.EngagementAndContentSharing()
    assert report.name == "Engagement and content sharing"
    d = ["sharingService", "subscribedStatus"]
    f = {"country": "US", "video": "fn849bng984b", "subscribedStatus": "SUBSCRIBED"}
    m = ["shares"]
    s = ["shares"]
    report.validate(d, f, m, s)


def test_engagement_and_content_sharing_2():
    report = rt.EngagementAndContentSharing()
    assert report.name == "Engagement and content sharing"
    d = ["sharingService"]
    f = {"continent": "002", "group": "fn849bng984b"}
    m = ["shares"]
    s = ["shares"]
    report.validate(d, f, m, s)


def test_engagement_and_content_sharing_3():
    report = rt.EngagementAndContentSharing()
    assert report.name == "Engagement and content sharing"
    d = ["sharingService"]
    f = {"subContinent": "014"}
    m = ["shares"]
    s = ["shares"]
    report.validate(d, f, m, s)


def test_engagement_and_content_sharing_4():
    report = rt.EngagementAndContentSharing()
    assert report.name == "Engagement and content sharing"
    d = ["sharingService"]
    f = {}
    m = ["shares"]
    s = ["shares"]
    report.validate(d, f, m, s)


# AUDIENCE RETENTION


def test_audience_retention_1():
    report = rt.AudienceRetention()
    assert report.name == "Audience retention"
    d = ["elapsedVideoTimeRatio"]
    f = {"video": "fn849bng984b", "audienceType": "ORGANIC"}
    m = ["audienceWatchRatio", "relativeRetentionPerformance"]
    s = ["audienceWatchRatio", "relativeRetentionPerformance"]
    report.validate(d, f, m, s)


def test_audience_retention_2():
    report = rt.AudienceRetention()
    assert report.name == "Audience retention"
    d = ["elapsedVideoTimeRatio"]
    f = {
        "video": "fn849bng984b",
        "audienceType": "ORGANIC",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = ["audienceWatchRatio", "relativeRetentionPerformance"]
    s = ["audienceWatchRatio", "relativeRetentionPerformance"]
    report.validate(d, f, m, s)


def test_audience_retention_3():
    report = rt.AudienceRetention()
    assert report.name == "Audience retention"
    d = ["elapsedVideoTimeRatio"]
    f = {
        "video": "fn849bng984b",
        "audienceType": "ORGANIC",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = ["audienceWatchRatio", "relativeRetentionPerformance"]
    s = ["audienceWatchRatio", "relativeRetentionPerformance"]
    report.validate(d, f, m, s)


def test_audience_retention_4():
    report = rt.AudienceRetention()
    assert report.name == "Audience retention"
    d = ["elapsedVideoTimeRatio"]
    f = {"video": "fn849bng984b"}
    m = ["audienceWatchRatio", "relativeRetentionPerformance"]
    s = ["audienceWatchRatio", "relativeRetentionPerformance"]
    report.validate(d, f, m, s)


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


# TOP VIDEOS BY REGION


def test_top_videos_regional_1():
    report = rt.TopVideosRegional()
    assert report.name == "Top videos by region"
    d = ["video"]
    f = {"country": "US"}
    m = data.ALL_VIDEO_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_EXTRA_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_regional_2():
    report = rt.TopVideosRegional()
    assert report.name == "Top videos by region"
    d = ["video"]
    f = {"continent": "002"}
    m = data.ALL_VIDEO_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_EXTRA_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_regional_3():
    report = rt.TopVideosRegional()
    assert report.name == "Top videos by region"
    d = ["video"]
    f = {"subContinent": "014"}
    m = data.ALL_VIDEO_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_EXTRA_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_regional_4():
    report = rt.TopVideosRegional()
    assert report.name == "Top videos by region"
    d = ["video"]
    f = {}
    m = data.ALL_VIDEO_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_EXTRA_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


# TOP VIDEOS BY STATE


def test_top_videos_us_1():
    report = rt.TopVideosUS()
    assert report.name == "Top videos by state"
    d = ["video"]
    f = {"province": "US-OH", "subscribedStatus": "SUBSCRIBED"}
    m = data.ALL_PROVINCE_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_us_2():
    report = rt.TopVideosUS()
    assert report.name == "Top videos by state"
    d = ["video"]
    f = {"province": "US-OH"}
    m = data.ALL_PROVINCE_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


# TOP VIDEOS BY SUBSCRIPTION STATUS


def test_top_videos_subscribed_1():
    report = rt.TopVideosSubscribed()
    assert report.name == "Top videos by subscription status"
    d = ["video"]
    f = {"subscribedStatus": "SUBSCRIBED", "country": "US"}
    m = data.SUBSCRIPTION_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_subscribed_2():
    report = rt.TopVideosSubscribed()
    assert report.name == "Top videos by subscription status"
    d = ["video"]
    f = {"continent": "002"}
    m = data.SUBSCRIPTION_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_subscribed_3():
    report = rt.TopVideosSubscribed()
    assert report.name == "Top videos by subscription status"
    d = ["video"]
    f = {"subContinent": "014"}
    m = data.SUBSCRIPTION_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


# TOP VIDEOS BY SUBSCRIPTION STATUS


def test_top_videos_youtube_product_1():
    report = rt.TopVideosYouTubeProduct()
    assert report.name == "Top videos by YouTube product"
    d = ["video"]
    f = {"country": "US", "subscribedStatus": "SUBSCRIBED"}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_youtube_product_2():
    report = rt.TopVideosYouTubeProduct()
    assert report.name == "Top videos by YouTube product"
    d = ["video"]
    f = {
        "province": "US-OH",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_youtube_product_3():
    report = rt.TopVideosYouTubeProduct()
    assert report.name == "Top videos by YouTube product"
    d = ["video"]
    f = {"continent": "002"}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_youtube_product_4():
    report = rt.TopVideosYouTubeProduct()
    assert report.name == "Top videos by YouTube product"
    d = ["video"]
    f = {"subContinent": "014"}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_youtube_product_5():
    report = rt.TopVideosYouTubeProduct()
    assert report.name == "Top videos by YouTube product"
    d = ["video"]
    f = {}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


# TOP VIDEOS BY PLAYBACK DETAIL


def test_top_videos_playback_detail_1():
    report = rt.TopVideosPlaybackDetail()
    assert report.name == "Top videos by playback detail"
    d = ["video"]
    f = {"country": "US", "liveOrOnDemand": "LIVE"}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_playback_detail_2():
    report = rt.TopVideosPlaybackDetail()
    assert report.name == "Top videos by playback detail"
    d = ["video"]
    f = {
        "province": "US-OH",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_playback_detail_3():
    report = rt.TopVideosPlaybackDetail()
    assert report.name == "Top videos by playback detail"
    d = ["video"]
    f = {
        "continent": "002",
        "liveOrOnDemand": "LIVE",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_playback_detail_4():
    report = rt.TopVideosPlaybackDetail()
    assert report.name == "Top videos by playback detail"
    d = ["video"]
    f = {"subContinent": "014"}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_videos_playback_detail_5():
    report = rt.TopVideosPlaybackDetail()
    assert report.name == "Top videos by playback detail"
    d = ["video"]
    f = {}
    m = data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)
