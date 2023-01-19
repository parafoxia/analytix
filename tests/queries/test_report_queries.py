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

import datetime as dt

import pytest

import analytix
from analytix.errors import InvalidRequest
from analytix.queries import ReportQuery
from analytix.reports import types as rt


def test_create_defaults():
    query = ReportQuery()
    assert query.dimensions == ()
    assert query.filters == {}
    assert query.metrics == ()
    assert query.sort_options == ()
    assert query.max_results == 0
    assert query._start_date == dt.date.today() - dt.timedelta(days=28)
    assert query._end_date == dt.date.today()
    assert query.currency == "USD"
    assert query.start_index == 1
    assert query._include_historical_data == False
    assert query.rtype is None


def test_create_custom():
    query = ReportQuery(
        dimensions=["day", "country"],
        filters={"continent": "002"},
        metrics=["views", "likes", "comments"],
        sort_options=["shares", "dislikes"],
        max_results=200,
        start_date=dt.date(2021, 1, 1),
        end_date=dt.date(2021, 12, 31),
        currency="GBP",
        start_index=10,
        include_historical_data=True,
    )
    assert query.dimensions == ["day", "country"]
    assert query.filters == {"continent": "002"}
    assert query.metrics == ["views", "likes", "comments"]
    assert query.sort_options == ["shares", "dislikes"]
    assert query.max_results == 200
    assert query._start_date == dt.date(2021, 1, 1)
    assert query._end_date == dt.date(2021, 12, 31)
    assert query.currency == "GBP"
    assert query.start_index == 10
    assert query._include_historical_data == True
    assert query.rtype is None


@pytest.fixture()
async def query() -> ReportQuery:
    return ReportQuery(
        dimensions=["day", "country"],
        filters={"continent": "002", "deviceType": "MOBILE"},
        metrics=["views", "likes", "comments"],
        sort_options=["shares", "dislikes"],
        start_date=dt.date(2021, 1, 1),
        end_date=dt.date(2021, 12, 31),
    )


def test_start_date_property(query):
    assert query.start_date == "2021-01-01"


def test_end_date_property(query):
    assert query.end_date == "2021-12-31"


def test_include_historical_data_property(query):
    assert query.include_historical_data == "false"


def test_url_property(query):
    assert query.url == analytix.API_REPORTS_URL + (
        "ids=channel==MINE"
        "&dimensions=day,country"
        "&filters=continent==002;deviceType==MOBILE"
        "&metrics=views,likes,comments"
        "&sort=shares,dislikes"
        "&maxResults=0"
        "&startDate=2021-01-01"
        "&endDate=2021-12-31"
        "&currency=USD"
        "&startIndex=1"
        "&includeHistoricalData=false"
    )


def test_validate_max_results():
    query = ReportQuery(max_results=-1)
    with pytest.raises(
        InvalidRequest,
        match=r"the max results should be non-negative \(0 for unlimited results\)",
    ):
        query.validate()


def test_validate_start_date_is_date():
    query = ReportQuery(start_date="2021-01-01")  # type: ignore
    with pytest.raises(InvalidRequest, match="expected start date as date object"):
        query.validate()


def test_validate_end_date_is_date():
    query = ReportQuery(
        end_date="2021-01-01", start_date=dt.date(2021, 1, 1)  # type: ignore
    )
    with pytest.raises(InvalidRequest, match="expected end date as date object"):
        query.validate()


def test_validate_end_date_gt_start_date():
    query = ReportQuery(end_date=dt.date(2021, 1, 1), start_date=dt.date(2021, 1, 2))
    with pytest.raises(
        InvalidRequest, match="the start date should be earlier than the end date"
    ):
        query.validate()


def test_validate_currency():
    query = ReportQuery(currency="LOL")
    with pytest.raises(InvalidRequest, match="expected a valid ISO 4217 currency code"):
        query.validate()


def test_validate_start_index():
    query = ReportQuery(start_index=0)
    with pytest.raises(InvalidRequest, match="the start index should be positive"):
        query.validate()


def test_validate_months_are_corrected():
    query = ReportQuery(
        dimensions=["month"],
        start_date=dt.date(2021, 4, 2),
        end_date=dt.date(2022, 3, 31),
    )
    query.validate()
    assert query._start_date == dt.date(2021, 4, 1)
    assert query._end_date == dt.date(2022, 3, 1)


def test_determine_ad_performance():
    query = ReportQuery(dimensions=["adType"])
    assert isinstance(query.determine_report_type(), rt.AdPerformance)


def test_determine_engagement_and_content_sharing():
    query = ReportQuery(dimensions=["sharingService"])
    assert isinstance(query.determine_report_type(), rt.EngagementAndContentSharing)


def test_determine_audience_retention():
    query = ReportQuery(dimensions=["elapsedVideoTimeRatio"])
    assert isinstance(query.determine_report_type(), rt.AudienceRetention)


def test_determine_top_playlists():
    query = ReportQuery(dimensions=["playlist"])
    assert isinstance(query.determine_report_type(), rt.TopPlaylists)


def test_determine_geography_based_activity_by_city():
    query = ReportQuery(dimensions=["city"])
    assert isinstance(query.determine_report_type(), rt.GeographyBasedActivityByCity)


def test_determine_playback_location():
    query = ReportQuery(dimensions=["insightPlaybackLocationType"])
    assert isinstance(query.determine_report_type(), rt.PlaybackLocation)


def test_determine_playback_location_playlist():
    query = ReportQuery(
        dimensions=["insightPlaybackLocationType"], filters={"isCurated": "1"}
    )
    assert isinstance(query.determine_report_type(), rt.PlaybackLocationPlaylist)


def test_determine_playback_location_detail():
    query = ReportQuery(dimensions=["insightPlaybackLocationDetail"])
    assert isinstance(query.determine_report_type(), rt.PlaybackLocationDetail)


def test_determine_playback_location_detail_playlist():
    query = ReportQuery(
        dimensions=["insightPlaybackLocationDetail"], filters={"isCurated": "1"}
    )
    assert isinstance(query.determine_report_type(), rt.PlaybackLocationDetailPlaylist)


def test_determine_traffic_source():
    query = ReportQuery(dimensions=["insightTrafficSourceType"])
    assert isinstance(query.determine_report_type(), rt.TrafficSource)


def test_determine_traffic_source_playlist():
    query = ReportQuery(
        dimensions=["insightTrafficSourceType"], filters={"isCurated": "1"}
    )
    assert isinstance(query.determine_report_type(), rt.TrafficSourcePlaylist)


def test_determine_traffic_source_detail():
    query = ReportQuery(dimensions=["insightTrafficSourceDetail"])
    assert isinstance(query.determine_report_type(), rt.TrafficSourceDetail)


def test_determine_traffic_source_detail_playlist():
    query = ReportQuery(
        dimensions=["insightTrafficSourceDetail"], filters={"isCurated": "1"}
    )
    assert isinstance(query.determine_report_type(), rt.TrafficSourceDetailPlaylist)


def test_determine_viewer_demographics():
    query = ReportQuery(dimensions=["ageGroup"])
    assert isinstance(query.determine_report_type(), rt.ViewerDemographics)


def test_determine_viewer_demographics_playlist():
    query = ReportQuery(dimensions=["gender"], filters={"isCurated": "1"})
    assert isinstance(query.determine_report_type(), rt.ViewerDemographicsPlaylist)


def test_determine_device_type():
    query = ReportQuery(dimensions=["deviceType"])
    assert isinstance(query.determine_report_type(), rt.DeviceType)


def test_determine_device_type_playlist():
    query = ReportQuery(dimensions=["deviceType"], filters={"isCurated": "1"})
    assert isinstance(query.determine_report_type(), rt.DeviceTypePlaylist)


def test_determine_operating_system():
    query = ReportQuery(dimensions=["operatingSystem"])
    assert isinstance(query.determine_report_type(), rt.OperatingSystem)


def test_determine_operating_system_playlist():
    query = ReportQuery(dimensions=["operatingSystem"], filters={"isCurated": "1"})
    assert isinstance(query.determine_report_type(), rt.OperatingSystemPlaylist)


def test_determine_device_type_and_operating_system():
    query = ReportQuery(dimensions=["deviceType", "operatingSystem"])
    assert isinstance(query.determine_report_type(), rt.DeviceTypeAndOperatingSystem)


def test_determine_device_type_and_operating_system_playlist():
    query = ReportQuery(
        dimensions=["deviceType", "operatingSystem"], filters={"isCurated": "1"}
    )
    assert isinstance(
        query.determine_report_type(), rt.DeviceTypeAndOperatingSystemPlaylist
    )


def test_determine_top_videos_us():
    query = ReportQuery(dimensions=["video"], filters={"province": "US-OH"})
    assert isinstance(query.determine_report_type(), rt.TopVideosUS)


def test_determine_top_videos_youtube_product():
    query = ReportQuery(
        dimensions=["video"],
        filters={"subscribedStatus": "SUBSCRIBED", "youtubeProduct": "CORE"},
        metrics=["averageViewPercentage"],
    )
    assert isinstance(query.determine_report_type(), rt.TopVideosYouTubeProduct)


def test_determine_top_videos_subscribed():
    query = ReportQuery(
        dimensions=["video"], filters={"subscribedStatus": "SUBSCRIBED"}
    )
    assert isinstance(query.determine_report_type(), rt.TopVideosSubscribed)


def test_determine_top_videos_regional():
    query = ReportQuery(dimensions=["video"])
    assert isinstance(query.determine_report_type(), rt.TopVideosRegional)


def test_determine_top_videos_playback_detail():
    query = ReportQuery(
        dimensions=["video"],
        filters={"subscribedStatus": "SUBSCRIBED", "youtubeProduct": "CORE"},
    )
    assert isinstance(query.determine_report_type(), rt.TopVideosPlaybackDetail)


def test_determine_playback_details_live_geography_based_1():
    query = ReportQuery(dimensions=["country", "liveOrOnDemand"])
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsLiveGeographyBased
    )


def test_determine_playback_details_live_geography_based_2():
    query = ReportQuery(dimensions=["country"], filters={"liveOrOnDemand": "LIVE"})
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsLiveGeographyBased
    )


def test_determine_geography_based_activity_playlist():
    query = ReportQuery(dimensions=["country"], filters={"isCurated": "1"})
    assert isinstance(query.determine_report_type(), rt.GeographyBasedActivityPlaylist)


def test_determine_playback_details_view_percentage_geography_based_1():
    query = ReportQuery(dimensions=["country", "subscribedStatus"])
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsViewPercentageGeographyBased
    )


def test_determine_playback_details_view_percentage_geography_based_2():
    query = ReportQuery(
        dimensions=["country"], filters={"subscribedStatus": "SUBSCRIBED"}
    )
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsViewPercentageGeographyBased
    )


def test_determine_playback_details_view_percentage_geography_based_3():
    query = ReportQuery(dimensions=["country", "youtubeProduct"])
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsViewPercentageGeographyBased
    )


def test_determine_playback_details_view_percentage_geography_based_4():
    query = ReportQuery(dimensions=["country"], filters={"youtubeProduct": "CORE"})
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsViewPercentageGeographyBased
    )


def test_determine_geography_based_activity():
    query = ReportQuery(dimensions=["country"])
    assert isinstance(query.determine_report_type(), rt.GeographyBasedActivity)


def test_determine_playback_details_live_geography_based_us_1():
    query = ReportQuery(dimensions=["province", "liveOrOnDemand"])
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsLiveGeographyBasedUS
    )


def test_determine_playback_details_live_geography_based_us_2():
    query = ReportQuery(dimensions=["province"], filters={"liveOrOnDemand": "LIVE"})
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsLiveGeographyBasedUS
    )


def test_determine_geography_based_activity_us_playlist():
    query = ReportQuery(dimensions=["province"], filters={"isCurated": "1"})
    assert isinstance(
        query.determine_report_type(), rt.GeographyBasedActivityUSPlaylist
    )


def test_determine_playback_details_view_percentage_geography_based_us_1():
    query = ReportQuery(dimensions=["province", "subscribedStatus"])
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsViewPercentageGeographyBasedUS
    )


def test_determine_playback_details_view_percentage_geography_based_us_2():
    query = ReportQuery(
        dimensions=["province"], filters={"subscribedStatus": "SUBSCRIBED"}
    )
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsViewPercentageGeographyBasedUS
    )


def test_determine_playback_details_view_percentage_geography_based_us_3():
    query = ReportQuery(dimensions=["province", "youtubeProduct"])
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsViewPercentageGeographyBasedUS
    )


def test_determine_playback_details_view_percentage_geography_based_us_4():
    query = ReportQuery(dimensions=["province"], filters={"youtubeProduct": "CORE"})
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsViewPercentageGeographyBasedUS
    )


def test_determine_geography_based_activity_us():
    query = ReportQuery(dimensions=["province"])
    assert isinstance(query.determine_report_type(), rt.GeographyBasedActivityUS)


def test_determine_playback_details_view_percentage_time_based_1():
    query = ReportQuery(dimensions=["youtubeProduct"])
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsViewPercentageTimeBased
    )


def test_determine_playback_details_view_percentage_time_based_2():
    query = ReportQuery(filters={"youtubeProduct": "CORE"})
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsViewPercentageTimeBased
    )


def test_determine_playback_details_live_time_based_1():
    query = ReportQuery(dimensions=["youtubeProduct", "liveOrOnDemand"])
    assert isinstance(query.determine_report_type(), rt.PlaybackDetailsLiveTimeBased)


def test_determine_playback_details_live_time_based_2():
    query = ReportQuery(filters={"youtubeProduct": "CORE", "liveOrOnDemand": "LIVE"})
    assert isinstance(query.determine_report_type(), rt.PlaybackDetailsLiveTimeBased)


def test_determine_playback_details_live_time_based_3():
    query = ReportQuery(dimensions=["liveOrOnDemand"])
    assert isinstance(query.determine_report_type(), rt.PlaybackDetailsLiveTimeBased)


def test_determine_playback_details_live_time_based_4():
    query = ReportQuery(filters={"liveOrOnDemand": "LIVE"})
    assert isinstance(query.determine_report_type(), rt.PlaybackDetailsLiveTimeBased)


def test_determine_subscribed_status():
    query = ReportQuery(dimensions=["subscribedStatus"])
    assert isinstance(query.determine_report_type(), rt.PlaybackDetailsSubscribedStatus)


def test_determine_subscribed_status_us():
    query = ReportQuery(dimensions=["subscribedStatus"], filters={"province": "US-OH"})
    assert isinstance(
        query.determine_report_type(), rt.PlaybackDetailsSubscribedStatusUS
    )


def test_determine_time_based_activity_1():
    query = ReportQuery(dimensions=["day"])
    assert isinstance(query.determine_report_type(), rt.TimeBasedActivity)


def test_determine_time_based_activity_2():
    query = ReportQuery(dimensions=["month"])
    assert isinstance(query.determine_report_type(), rt.TimeBasedActivity)


def test_determine_time_based_activity_playlist_1():
    query = ReportQuery(dimensions=["day"], filters={"isCurated": "1"})
    assert isinstance(query.determine_report_type(), rt.TimeBasedActivityPlaylist)


def test_determine_time_based_activity_playlist_2():
    query = ReportQuery(dimensions=["month"], filters={"isCurated": "1"})
    assert isinstance(query.determine_report_type(), rt.TimeBasedActivityPlaylist)


def test_determine_time_based_activity_us_1():
    query = ReportQuery(dimensions=["day"], filters={"province": "US-OH"})
    assert isinstance(query.determine_report_type(), rt.TimeBasedActivityUS)


def test_determine_time_based_activity_us_2():
    query = ReportQuery(dimensions=["month"], filters={"province": "US-OH"})
    assert isinstance(query.determine_report_type(), rt.TimeBasedActivityUS)


def test_determine_basic_user_activity_playlist():
    query = ReportQuery(filters={"isCurated": "1"})
    assert isinstance(query.determine_report_type(), rt.BasicUserActivityPlaylist)


def test_determine_basic_user_activity_us():
    query = ReportQuery(filters={"province": "US-OH"})
    assert isinstance(query.determine_report_type(), rt.BasicUserActivityUS)


def test_determine_basic_user_activity():
    query = ReportQuery()
    assert isinstance(query.determine_report_type(), rt.BasicUserActivity)
