# Copyright (c) 2021, Ethan Henderson
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

import datetime as dt
import inspect

import pytest

from analytix import YouTubeAnalytics
from analytix.errors import HTTPError, InvalidRequest


@pytest.fixture()
def client():
    client = YouTubeAnalytics.from_file("./secrets/secrets.json")
    client.authorise()
    return client


def test_basic_user_activity(client):
    try:
        report = client.retrieve(dt.date(2021, 1, 1))
        assert report.type == "Basic user activity"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_basic_user_activity_us(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1), filters={"province": "US-OH"}
        )
        assert report.type == "Basic user activity (US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_time_based_activity(client):
    try:
        report = client.retrieve(dt.date(2021, 1, 1), dimensions=("day",))
        assert report.type == "Time-based activity"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_time_based_activity_us(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day",),
            filters={"province": "US-OH"},
        )
        assert report.type == "Time-based activity (US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_geography_based_activity(client):
    try:
        report = client.retrieve(dt.date(2021, 1, 1), dimensions=("country",))
        assert report.type == "Geography-based activity"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_geography_based_activity_us(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("province",),
            filters={"country": "US"},
        )
        assert report.type == "Geography-based activity (US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_user_activity_by_subscribed_status(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("subscribedStatus",),
        )
        assert report.type == "User activity by subscribed status"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_user_activity_by_subscribed_status_us(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("subscribedStatus",),
            filters={"province": "US-OH"},
        )
        assert report.type == "User activity by subscribed status (US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_time_based_playback_details_live(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=(
                "liveOrOnDemand",
                "youtubeProduct",
            ),
        )
        assert report.type == "Time-based playback details (live)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_time_based_playback_details_view_percentage(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("youtubeProduct",),
        )
        assert report.type == "Time-based playback details (view percentage)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_geography_based_playback_details_live(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=(
                "country",
                "liveOrOnDemand",
            ),
        )
        assert report.type == "Geography-based playback details (live)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_geography_based_playback_details_view_percentage(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=(
                "country",
                "subscribedStatus",
            ),
        )
        assert (
            report.type == "Geography-based playback details (view percentage)"
        )
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_geography_based_playback_details_live_us(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=(
                "province",
                "liveOrOnDemand",
            ),
            filters={"country": "US"},
        )
        assert report.type == "Geography-based playback details (live, US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_geography_based_playback_details_view_percentage_us(
    client,
):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=(
                "province",
                "subscribedStatus",
            ),
            filters={"country": "US"},
        )
        assert (
            report.type
            == "Geography-based playback details (view percentage, US)"
        )
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_playback_locations(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightPlaybackLocationType",),
        )
        assert report.type == "Playback locations"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_playback_locations_detailed(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightPlaybackLocationDetail",),
            filters={"insightPlaybackLocationType": "EMBEDDED"},
            sort_by=("-views",),
            max_results=25,
        )
        assert report.type == "Playback locations (detailed)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_traffic_sources(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightTrafficSourceType",),
        )
        assert report.type == "Traffic sources"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_traffic_sources_detailed(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightTrafficSourceDetail",),
            filters={"insightTrafficSourceType": "YT_CHANNEL"},
            sort_by=("-views",),
            max_results=25,
        )
        assert report.type == "Traffic sources (detailed)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_device_types(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("deviceType",),
        )
        assert report.type == "Device types"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_operating_systems(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("operatingSystem",),
        )
        assert report.type == "Operating systems"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_device_types_and_operating_systems(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("deviceType", "operatingSystem"),
        )
        assert report.type == "Device types and operating systems"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_viewer_demographics(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("ageGroup",),
        )
        assert report.type == "Viewer demographics"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_engagement_and_content_sharing(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1), dimensions=("sharingService",)
        )
        assert report.type == "Engagement and content sharing"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_audience_retention(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("elapsedVideoTimeRatio",),
            filters={"video": "jsQ3TUDcmos"},
        )
        assert report.type == "Audience retention"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_top_videos_by_region(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("video",),
            sort_by=("-views",),
            max_results=200,
        )
        assert report.type == "Top videos by region"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_top_videos_by_state(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("video",),
            filters={"province": "US-OH"},
            sort_by=("-views",),
            max_results=200,
        )
        assert report.type == "Top videos by state"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_top_videos_by_subscription_status(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("video",),
            filters={"subscribedStatus": "SUBSCRIBED"},
            sort_by=("-views",),
            max_results=200,
        )
        assert report.type == "Top videos by subscription status"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_top_videos_by_youtube_product(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("video",),
            metrics=(
                "views",
                "averageViewPercentage",
            ),
            filters={
                "subscribedStatus": "SUBSCRIBED",
                "youtubeProduct": "CORE",
            },
            sort_by=("-views",),
            max_results=200,
        )
        assert report.type == "Top videos by YouTube product"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_top_videos_by_playback_detail(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("video",),
            filters={
                "liveOrOnDemand": "ON_DEMAND",
                "subscribedStatus": "SUBSCRIBED",
                "youtubeProduct": "CORE",
            },
            sort_by=("-views",),
            max_results=200,
        )
        assert report.type == "Top videos by playback detail"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_basic_user_activity_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1), filters={"isCurated": "1"}
        )
        assert report.type == "Basic user activity for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_time_based_activity_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Time-based activity for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_geography_based_activity_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("country",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Geography-based activity for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_geography_based_activity_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("province",),
            filters={"isCurated": "1", "country": "US"},
        )
        assert report.type == "Geography-based activity for playlists (US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_playback_locations_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightPlaybackLocationType",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Playback locations for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_playback_locations_for_playlists_detailed(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightPlaybackLocationDetail",),
            filters={
                "isCurated": "1",
                "insightPlaybackLocationType": "EMBEDDED",
            },
            sort_by=("-views",),
            max_results=25,
        )
        assert report.type == "Playback locations for playlists (detailed)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_traffic_sources_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightTrafficSourceType",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Traffic sources for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_traffic_sources_for_playlists_detailed(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightTrafficSourceDetail",),
            filters={
                "isCurated": "1",
                "insightTrafficSourceType": "YT_CHANNEL",
            },
            sort_by=("-views",),
            max_results=25,
        )
        assert report.type == "Traffic sources for playlists (detailed)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_device_types_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("deviceType",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Device types for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_operating_systems_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("operatingSystem",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Operating systems for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_device_types_and_operating_systems_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("deviceType", "operatingSystem"),
            filters={"isCurated": "1"},
        )
        assert (
            report.type == "Device types and operating systems for playlists"
        )
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_viewer_demographics_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("ageGroup",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Viewer demographics for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_top_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("playlist",),
            filters={"isCurated": "1"},
            sort_by=("-views",),
            max_results=200,
        )
        assert report.type == "Top playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_ad_performance(client):
    try:
        report = client.retrieve(dt.date(2021, 1, 1), dimensions=("adType",))
        assert report.type == "Ad performance"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"
