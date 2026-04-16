# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import datetime as dt
import re
import warnings

import pytest

from analytix.auth import Scopes
from analytix.errors import InvalidRequest
from analytix.queries import API_REPORTS_URL
from analytix.queries import ReportQuery
from analytix.reports.types.ad import AdPerformance
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
from analytix.reports.types.video import AudienceRetention
from analytix.reports.types.video import BasicUserActivity
from analytix.reports.types.video import BasicUserActivityUS
from analytix.reports.types.video import DeviceType
from analytix.reports.types.video import DeviceTypeAndOperatingSystem
from analytix.reports.types.video import EngagementAndContentSharing
from analytix.reports.types.video import GeographyBasedActivity
from analytix.reports.types.video import GeographyBasedActivityByCity
from analytix.reports.types.video import GeographyBasedActivityUS
from analytix.reports.types.video import OperatingSystem
from analytix.reports.types.video import PlaybackDetailsLiveGeographyBased
from analytix.reports.types.video import PlaybackDetailsLiveGeographyBasedUS
from analytix.reports.types.video import PlaybackDetailsLiveTimeBased
from analytix.reports.types.video import PlaybackDetailsSubscribedStatus
from analytix.reports.types.video import PlaybackDetailsSubscribedStatusUS
from analytix.reports.types.video import PlaybackDetailsViewPercentageGeographyBased
from analytix.reports.types.video import PlaybackDetailsViewPercentageGeographyBasedUS
from analytix.reports.types.video import PlaybackDetailsViewPercentageTimeBased
from analytix.reports.types.video import PlaybackLocation
from analytix.reports.types.video import PlaybackLocationDetail
from analytix.reports.types.video import TimeBasedActivity
from analytix.reports.types.video import TimeBasedActivityUS
from analytix.reports.types.video import TopVideosPlaybackDetail
from analytix.reports.types.video import TopVideosRegional
from analytix.reports.types.video import TopVideosSubscribed
from analytix.reports.types.video import TopVideosUS
from analytix.reports.types.video import TopVideosYouTubeProduct
from analytix.reports.types.video import TrafficSource
from analytix.reports.types.video import TrafficSourceDetail
from analytix.reports.types.video import ViewerDemographics
from analytix.warnings import InvalidMonthFormatWarning


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


def test_start_date_property(query):
    assert query.start_date == "2021-01-01"


def test_end_date_property(query):
    assert query.end_date == "2021-12-31"


def test_include_historical_data_property(query):
    assert query.include_historical_data == "false"


def test_url_property(query):
    assert query.url == API_REPORTS_URL + (
        "?ids=channel==MINE"
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
        query.validate(Scopes.ALL)


def test_validate_start_date_is_date():
    query = ReportQuery(start_date="2021-01-01")  # type: ignore
    with pytest.raises(InvalidRequest, match="expected start date as date object"):
        query.validate(Scopes.ALL)


def test_validate_end_date_is_date():
    query = ReportQuery(
        end_date="2021-01-01",
        start_date=dt.date(2021, 1, 1),  # type: ignore
    )
    with pytest.raises(InvalidRequest, match="expected end date as date object"):
        query.validate(Scopes.ALL)


def test_validate_end_date_gt_start_date():
    query = ReportQuery(end_date=dt.date(2021, 1, 1), start_date=dt.date(2021, 1, 2))
    with pytest.raises(
        InvalidRequest,
        match="the start date should be earlier than the end date",
    ):
        query.validate(Scopes.ALL)


def test_validate_currency():
    query = ReportQuery(currency="LOL")
    with pytest.raises(
        InvalidRequest,
        match="expected a valid ISO 4217 currency code, got 'LOL'",
    ):
        query.validate(Scopes.ALL)


def test_validate_start_index():
    query = ReportQuery(start_index=0)
    with pytest.raises(InvalidRequest, match="the start index should be positive"):
        query.validate(Scopes.ALL)


def test_validate_months_are_corrected():
    query = ReportQuery(
        dimensions=["month"],
        start_date=dt.date(2021, 4, 2),
        end_date=dt.date(2022, 3, 31),
    )

    with warnings.catch_warnings(record=True) as warns:
        query.validate(Scopes.ALL)
        assert len(warns) == 1
        assert issubclass(warns[-1].category, InvalidMonthFormatWarning)
        assert (
            "Correcting start and end dates -- if 'month' is passed as a dimension, these should always be the first day of the month"
            in str(warns[-1].message)
        )

    assert query._start_date == dt.date(2021, 4, 1)
    assert query._end_date == dt.date(2022, 3, 1)


def test_validate_all_sort_options_are_metrics_singular():
    query = ReportQuery(
        metrics=("likes",),
        sort_options=("-views",),
    )
    with pytest.raises(
        InvalidRequest,
        match=re.escape("sort option 'views' is not part of the given metrics"),
    ):
        query.validate(Scopes.ALL)


def test_validate_all_sort_options_are_metrics_plural():
    query = ReportQuery(
        metrics=("likes",),
        sort_options=("-views", "comments"),
    )
    with pytest.raises(
        InvalidRequest,
        match=re.escape(
            "sort options 'comments' and 'views' are not part of the given metrics",
        ),
    ):
        query.validate(Scopes.ALL)


def test_validate_respects_readonly_scope():
    query = ReportQuery(metrics=("views", "likes", "cpm", "grossRevenue"))
    query.validate(Scopes.READONLY)
    assert query.metrics == ["views", "likes"]


def test_validate_respects_monetary_readonly_scope():
    query = ReportQuery(metrics=("views", "likes", "cpm", "grossRevenue"))
    query.validate(Scopes.MONETARY_READONLY)
    assert query.metrics == ["cpm", "grossRevenue"]


def test_determine_is_new_playlist_report_playlist_dimension():
    query = ReportQuery(dimensions=["playlist"])
    assert query._is_playlist_report_type()


def test_determine_is_new_playlist_report_playlist_filter():
    query = ReportQuery(filters={"playlist": "a1b2c3d4e5"})
    assert query._is_playlist_report_type()


def test_determine_is_new_playlist_report_group_filter():
    query = ReportQuery(
        filters={"group": "a1b2c3d4e5"},
        metrics=("averageViewDuration",),
    )
    assert query._is_playlist_report_type()


def test_determine_is_new_playlist_report_group_filter_no_playlist_metrics():
    query = ReportQuery(dimensions={"group": "a1b2c3d4e5"})
    assert not query._is_playlist_report_type()


def test_determine_ad_performance():
    query = ReportQuery(dimensions=["adType"])
    assert isinstance(query.determine_report_type(), AdPerformance)


def test_determine_engagement_and_content_sharing():
    query = ReportQuery(dimensions=["sharingService"])
    assert isinstance(query.determine_report_type(), EngagementAndContentSharing)


def test_determine_audience_retention():
    query = ReportQuery(dimensions=["elapsedVideoTimeRatio"])
    assert isinstance(query.determine_report_type(), AudienceRetention)


def test_determine_top_playlists_deprecated():
    query = ReportQuery(dimensions=["playlist"], filters={"playlist": "a1b2c3d4e5"})
    assert isinstance(query.determine_report_type(), TopPlaylists)


def test_determine_geography_based_activity_by_city():
    query = ReportQuery(dimensions=["city"])
    assert isinstance(query.determine_report_type(), GeographyBasedActivityByCity)


def test_determine_playback_location():
    query = ReportQuery(dimensions=["insightPlaybackLocationType"])
    assert isinstance(query.determine_report_type(), PlaybackLocation)


def test_determine_playback_location_playlist_deprecated():
    query = ReportQuery(
        dimensions=["insightPlaybackLocationType"],
        filters={"playlist": "a1b2c3d4e5"},
    )
    assert isinstance(query.determine_report_type(), PlaybackLocationPlaylist)


def test_determine_playback_location_detail():
    query = ReportQuery(dimensions=["insightPlaybackLocationDetail"])
    assert isinstance(query.determine_report_type(), PlaybackLocationDetail)


def test_determine_playback_location_detail_playlist_deprecated():
    query = ReportQuery(
        dimensions=["insightPlaybackLocationDetail"],
        filters={"playlist": "a1b2c3d4e5"},
    )
    assert isinstance(query.determine_report_type(), PlaybackLocationDetailPlaylist)


def test_determine_traffic_source():
    query = ReportQuery(dimensions=["insightTrafficSourceType"])
    assert isinstance(query.determine_report_type(), TrafficSource)


def test_determine_traffic_source_playlist_deprecated():
    query = ReportQuery(
        dimensions=["insightTrafficSourceType"],
        filters={"playlist": "a1b2c3d4e5"},
    )
    assert isinstance(query.determine_report_type(), TrafficSourcePlaylist)


def test_determine_traffic_source_detail():
    query = ReportQuery(dimensions=["insightTrafficSourceDetail"])
    assert isinstance(query.determine_report_type(), TrafficSourceDetail)


def test_determine_traffic_source_detail_playlist_deprecated():
    query = ReportQuery(
        dimensions=["insightTrafficSourceDetail"],
        filters={"playlist": "a1b2c3d4e5"},
    )
    assert isinstance(query.determine_report_type(), TrafficSourceDetailPlaylist)


def test_determine_viewer_demographics():
    query = ReportQuery(dimensions=["ageGroup"])
    assert isinstance(query.determine_report_type(), ViewerDemographics)


def test_determine_viewer_demographics_playlist_deprecated():
    query = ReportQuery(dimensions=["gender"], filters={"playlist": "a1b2c3d4e5"})
    assert isinstance(query.determine_report_type(), ViewerDemographicsPlaylist)


def test_determine_device_type():
    query = ReportQuery(dimensions=["deviceType"])
    assert isinstance(query.determine_report_type(), DeviceType)


def test_determine_device_type_playlist_deprecated():
    query = ReportQuery(dimensions=["deviceType"], filters={"playlist": "a1b2c3d4e5"})
    assert isinstance(query.determine_report_type(), DeviceTypePlaylist)


def test_determine_operating_system():
    query = ReportQuery(dimensions=["operatingSystem"])
    assert isinstance(query.determine_report_type(), OperatingSystem)


def test_determine_operating_system_playlist_deprecated():
    query = ReportQuery(
        dimensions=["operatingSystem"],
        filters={"playlist": "a1b2c3d4e5"},
    )
    assert isinstance(query.determine_report_type(), OperatingSystemPlaylist)


def test_determine_device_type_and_operating_system():
    query = ReportQuery(dimensions=["deviceType", "operatingSystem"])
    assert isinstance(query.determine_report_type(), DeviceTypeAndOperatingSystem)


def test_determine_device_type_and_operating_system_playlist_deprecated():
    query = ReportQuery(
        dimensions=["deviceType", "operatingSystem"],
        filters={"playlist": "a1b2c3d4e5"},
    )
    assert isinstance(
        query.determine_report_type(),
        DeviceTypeAndOperatingSystemPlaylist,
    )


def test_determine_top_videos_us():
    query = ReportQuery(dimensions=["video"], filters={"province": "US-OH"})
    assert isinstance(query.determine_report_type(), TopVideosUS)


def test_determine_top_videos_youtube_product():
    query = ReportQuery(
        dimensions=["video"],
        filters={"subscribedStatus": "SUBSCRIBED", "youtubeProduct": "CORE"},
        metrics=["averageViewPercentage"],
    )
    assert isinstance(query.determine_report_type(), TopVideosYouTubeProduct)


def test_determine_top_videos_subscribed():
    query = ReportQuery(
        dimensions=["video"],
        filters={"subscribedStatus": "SUBSCRIBED"},
    )
    assert isinstance(query.determine_report_type(), TopVideosSubscribed)


def test_determine_top_videos_regional():
    query = ReportQuery(dimensions=["video"])
    assert isinstance(query.determine_report_type(), TopVideosRegional)


def test_determine_top_videos_playback_detail():
    query = ReportQuery(
        dimensions=["video"],
        filters={"subscribedStatus": "SUBSCRIBED", "youtubeProduct": "CORE"},
    )
    assert isinstance(query.determine_report_type(), TopVideosPlaybackDetail)


def test_determine_playback_details_live_geography_based_1():
    query = ReportQuery(dimensions=["country", "liveOrOnDemand"])
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsLiveGeographyBased,
    )


def test_determine_playback_details_live_geography_based_2():
    query = ReportQuery(dimensions=["country"], filters={"liveOrOnDemand": "LIVE"})
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsLiveGeographyBased,
    )


def test_determine_geography_based_activity_playlist_deprecated():
    query = ReportQuery(dimensions=["country"], filters={"playlist": "a1b2c3d4e5"})
    assert isinstance(query.determine_report_type(), GeographyBasedActivityPlaylist)


def test_determine_playback_details_view_percentage_geography_based_1():
    query = ReportQuery(dimensions=["country", "subscribedStatus"])
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsViewPercentageGeographyBased,
    )


def test_determine_playback_details_view_percentage_geography_based_2():
    query = ReportQuery(
        dimensions=["country"],
        filters={"subscribedStatus": "SUBSCRIBED"},
    )
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsViewPercentageGeographyBased,
    )


def test_determine_playback_details_view_percentage_geography_based_3():
    query = ReportQuery(dimensions=["country", "youtubeProduct"])
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsViewPercentageGeographyBased,
    )


def test_determine_playback_details_view_percentage_geography_based_4():
    query = ReportQuery(dimensions=["country"], filters={"youtubeProduct": "CORE"})
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsViewPercentageGeographyBased,
    )


def test_determine_geography_based_activity():
    query = ReportQuery(dimensions=["country"])
    assert isinstance(query.determine_report_type(), GeographyBasedActivity)


def test_determine_playback_details_live_geography_based_us_1():
    query = ReportQuery(dimensions=["province", "liveOrOnDemand"])
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsLiveGeographyBasedUS,
    )


def test_determine_playback_details_live_geography_based_us_2():
    query = ReportQuery(dimensions=["province"], filters={"liveOrOnDemand": "LIVE"})
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsLiveGeographyBasedUS,
    )


def test_determine_geography_based_activity_us_playlist_deprecated():
    query = ReportQuery(dimensions=["province"], filters={"playlist": "a1b2c3d4e5"})
    assert isinstance(
        query.determine_report_type(),
        GeographyBasedActivityUSPlaylist,
    )


def test_determine_playback_details_view_percentage_geography_based_us_1():
    query = ReportQuery(dimensions=["province", "subscribedStatus"])
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsViewPercentageGeographyBasedUS,
    )


def test_determine_playback_details_view_percentage_geography_based_us_2():
    query = ReportQuery(
        dimensions=["province"],
        filters={"subscribedStatus": "SUBSCRIBED"},
    )
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsViewPercentageGeographyBasedUS,
    )


def test_determine_playback_details_view_percentage_geography_based_us_3():
    query = ReportQuery(dimensions=["province", "youtubeProduct"])
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsViewPercentageGeographyBasedUS,
    )


def test_determine_playback_details_view_percentage_geography_based_us_4():
    query = ReportQuery(dimensions=["province"], filters={"youtubeProduct": "CORE"})
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsViewPercentageGeographyBasedUS,
    )


def test_determine_geography_based_activity_us():
    query = ReportQuery(dimensions=["province"])
    assert isinstance(query.determine_report_type(), GeographyBasedActivityUS)


def test_determine_playback_details_view_percentage_time_based_1():
    query = ReportQuery(dimensions=["youtubeProduct"])
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsViewPercentageTimeBased,
    )


def test_determine_playback_details_view_percentage_time_based_2():
    query = ReportQuery(filters={"youtubeProduct": "CORE"})
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsViewPercentageTimeBased,
    )


def test_determine_playback_details_live_time_based_1():
    query = ReportQuery(dimensions=["youtubeProduct", "liveOrOnDemand"])
    assert isinstance(query.determine_report_type(), PlaybackDetailsLiveTimeBased)


def test_determine_playback_details_live_time_based_2():
    query = ReportQuery(filters={"youtubeProduct": "CORE", "liveOrOnDemand": "LIVE"})
    assert isinstance(query.determine_report_type(), PlaybackDetailsLiveTimeBased)


def test_determine_playback_details_live_time_based_3():
    query = ReportQuery(dimensions=["liveOrOnDemand"])
    assert isinstance(query.determine_report_type(), PlaybackDetailsLiveTimeBased)


def test_determine_playback_details_live_time_based_4():
    query = ReportQuery(filters={"liveOrOnDemand": "LIVE"})
    assert isinstance(query.determine_report_type(), PlaybackDetailsLiveTimeBased)


def test_determine_subscribed_status():
    query = ReportQuery(dimensions=["subscribedStatus"])
    assert isinstance(query.determine_report_type(), PlaybackDetailsSubscribedStatus)


def test_determine_subscribed_status_us():
    query = ReportQuery(dimensions=["subscribedStatus"], filters={"province": "US-OH"})
    assert isinstance(
        query.determine_report_type(),
        PlaybackDetailsSubscribedStatusUS,
    )


def test_determine_time_based_activity_1():
    query = ReportQuery(dimensions=["day"])
    assert isinstance(query.determine_report_type(), TimeBasedActivity)


def test_determine_time_based_activity_2():
    query = ReportQuery(dimensions=["month"])
    assert isinstance(query.determine_report_type(), TimeBasedActivity)


def test_determine_time_based_activity_playlist_1_deprecated():
    query = ReportQuery(dimensions=["day"], filters={"playlist": "a1b2c3d4e5"})
    assert isinstance(query.determine_report_type(), TimeBasedActivityPlaylist)


def test_determine_time_based_activity_playlist_2_deprecated():
    query = ReportQuery(dimensions=["month"], filters={"playlist": "a1b2c3d4e5"})
    assert isinstance(query.determine_report_type(), TimeBasedActivityPlaylist)


def test_determine_time_based_activity_us_1():
    query = ReportQuery(dimensions=["day"], filters={"province": "US-OH"})
    assert isinstance(query.determine_report_type(), TimeBasedActivityUS)


def test_determine_time_based_activity_us_2():
    query = ReportQuery(dimensions=["month"], filters={"province": "US-OH"})
    assert isinstance(query.determine_report_type(), TimeBasedActivityUS)


def test_determine_basic_user_activity_playlist_deprecated():
    query = ReportQuery(filters={"playlist": "a1b2c3d4e5"})
    assert isinstance(query.determine_report_type(), BasicUserActivityPlaylist)


def test_determine_basic_user_activity_us():
    query = ReportQuery(filters={"province": "US-OH"})
    assert isinstance(query.determine_report_type(), BasicUserActivityUS)


def test_determine_basic_user_activity():
    query = ReportQuery()
    assert isinstance(query.determine_report_type(), BasicUserActivity)
