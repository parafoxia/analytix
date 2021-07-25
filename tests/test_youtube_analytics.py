import datetime as dt
import inspect
import json
import logging
import os

import pytest  # type: ignore

from analytix import YouTubeAnalytics
from analytix.errors import *


@pytest.fixture()
def client():
    client = YouTubeAnalytics.from_file("./secrets/secrets.json")
    client.authorise()
    return client


# Test client stuff


def test_client_project_id_match(client):
    with open("./secrets/secrets.json", mode="r", encoding="utf-8") as f:
        project_id = json.load(f)["installed"]["project_id"]
    assert client.project_id == project_id


# Test report functionality


def test_reports_shape(client):
    report = client.retrieve(
        dt.date(2021, 1, 1), dt.date(2021, 2, 28), dimensions=("day",)
    )
    assert report.shape == (59, 36)


def test_reports_max_results(client):
    report = client.retrieve(
        dt.date(2021, 1, 1),
        dt.date(2021, 2, 28),
        dimensions=("day",),
        max_results=20,
    )
    assert report.shape == (20, 36)


def test_reports_sort_ascending(client):
    report = client.retrieve(
        dt.date(2021, 1, 1),
        dt.date(2021, 2, 28),
        dimensions=("day",),
        sort_by=("views",),
    )
    arr = [r[1] for r in report.data["rows"]]
    assert arr == sorted(arr)


def test_reports_sort_descending(client):
    report = client.retrieve(
        dt.date(2021, 1, 1),
        dt.date(2021, 2, 28),
        dimensions=("day",),
        sort_by=("-views",),
    )
    arr = [r[1] for r in report.data["rows"]]
    assert arr == sorted(arr, reverse=True)


# Test report verification


def test_reports_verify_check_deprecated(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1), dimensions=("7DayTotals",)
        )
    assert (
        str(exc.value)
        == "the '7DayTotals' and '30DayTotals' dimensions were deprecated, "
        "and can no longer be used"
    )


def test_reports_verify_check_start_date(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve("2020/1/1", dimensions=("day",))
    assert str(exc.value).startswith("expected start date as date object")


def test_reports_verify_check_end_date(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), "2020/1/1")
    assert str(exc.value).startswith("expected end date as date object")


def test_reports_verify_check_end_date_greater(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), dt.date(2019, 1, 1))
    assert str(exc.value).startswith(
        "the start date should be earlier than the end date"
    )


def test_reports_verify_check_end_date_equal(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), dt.date(2020, 1, 1))
    assert str(exc.value).startswith(
        "the start date should be earlier than the end date"
    )


def test_reports_verify_check_currency(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), currency="ZZZ")
    assert str(exc.value).startswith(
        "expected valid currency as ISO 4217 code"
    )


def test_reports_verify_check_dimensions_type(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), dimensions="day")
    assert str(exc.value).startswith(
        "expected tuple, list, or set of dimensions"
    )


def test_reports_verify_check_filters_type(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), filters="country==US")
    assert str(exc.value).startswith("expected dict of filters")


def test_reports_verify_check_historical_bool(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2020, 1, 1), include_historical_data=1
        )
    assert str(exc.value).startswith(
        "expected bool for 'include_historical_data'"
    )


def test_reports_verify_check_max_results_int(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), max_results="5")
    assert str(exc.value).startswith("expected int for 'max_results'")


def test_reports_verify_check_max_results_too_low(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), max_results=-1)
    assert str(exc.value).startswith(
        "the maximum number of results should be no less than 0 "
        "(0 for unlimited results)"
    )


def test_reports_verify_check_sort_type(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2020, 1, 1), dimensions=("day",), sort_by="views"
        )
    assert str(exc.value).startswith(
        "expected tuple, list, or set of sorting columns"
    )


def test_reports_verify_check_start_index_int(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), start_index="5")
    assert str(exc.value).startswith("expected int for 'start_index'")


def test_reports_verify_check_start_index_too_low(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), start_index=0)
    assert str(exc.value).startswith(
        "the start index should be no less than 1"
    )


def test_reports_verify_check_metrics_type(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2020, 1, 1), dimensions=("day",), metrics="views"
        )
    assert str(exc.value).startswith("expected tuple, list, or set of metrics")


def test_reports_verify_check_invalid_dimension(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2021, 1, 1), dimensions=("test",))
    assert str(exc.value).startswith(
        "one or more dimensions you provided are invalid"
    )


def test_reports_verify_check_unsupported_dimension(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1), dimensions=("day", "country")
        )
    assert str(exc.value).startswith(
        "one or more dimensions you provided are not supported by the "
        "selected report type"
    )


def test_reports_verify_check_invalid_filter(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day",),
            filters={"test": "invalid"},
        )
    assert str(exc.value).startswith(
        "one or more filters you provided are invalid"
    )


def test_reports_verify_check_unsupported_filter(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("country",),
            filters={"province": "US-OH"},
        )
    assert str(exc.value).startswith(
        "one or more filters you provided are not supported by the "
        "selected report type"
    )


def test_reports_verify_check_invalid_filter_value(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day",),
            filters={"province": "US-XX"},
        )
    assert "is not a valid value for filter" in str(exc.value)


def test_reports_verify_check_invalid_metric(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day",),
            # Where "not" is the invalid metric, of course
            metrics=("jax", "is", "not", "cute"),
        )
    assert str(exc.value).startswith(
        "one or more metrics you provided are invalid"
    )


def test_reports_verify_check_unsupported_metric(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("subscribedStatus",),
            metrics=("views", "likes", "comments"),
        )
    assert str(exc.value).startswith(
        "one or more metrics you provided are not supported by the "
        "selected report type"
    )


def test_reports_verify_check_required_filter(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("province",),
        )
    assert str(exc.value).startswith("expected all filters from")


def test_reports_verify_check_required_filter_value(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("province",),
            filters={"country": "UK"},
        )
    assert (
        str(exc.value)
        == "filter 'country' must be set to 'US' for the selected report type"
    )


def test_reports_verify_check_exactly_one_dimension(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day", "month"),
        )
    assert str(exc.value).startswith("expected 1 dimension from")


def test_reports_verify_check_zero_or_one_dimensions(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("subscribedStatus", "day", "month"),
        )
    assert str(exc.value).startswith("expected 0 or 1 dimensions from")


def test_reports_verify_check_zero_or_one_filters(client):
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day",),
            filters={"country": "US", "continent": "002"},
        )
    assert str(exc.value).startswith("expected 0 or 1 filters from")


# Test dataframe stuff


def test_dataframe_day_is_datetime(client):
    import numpy as np
    import pandas as pd

    report = client.retrieve(dt.date(2021, 1, 1), dimensions=("day",))
    df = report.to_dataframe()
    assert pd.api.types.is_datetime64_ns_dtype(df["day"])


def test_dataframe_month_is_datetime(client):
    import numpy as np
    import pandas as pd

    report = client.retrieve(
        dt.date(2021, 1, 1), dt.date(2021, 6, 1), dimensions=("month",)
    )
    df = report.to_dataframe()
    assert pd.api.types.is_datetime64_ns_dtype(df["month"])


def test_dataframe_metrics_are_numeric(client):
    import numpy as np
    import pandas as pd

    report = client.retrieve(dt.date(2021, 1, 1), dimensions=("day",))
    df = report.to_dataframe()
    for series in df.iloc[:, 1:]:
        assert pd.api.types.is_numeric_dtype(df[series])


# Test file IO


def test_files_json(client):
    report = client.retrieve(
        dt.date(2021, 1, 1), dt.date(2021, 2, 28), dimensions=("day",)
    )
    report.to_json("./test.json")
    with open("./test.json", mode="r", encoding="utf-8") as f:
        data = json.load(f)
        assert [c["name"] for c in data["columnHeaders"]] == report.columns
        assert len(data["rows"]) == report.shape[0]

    os.remove("./test.json")


def test_files_csv(client):
    report = client.retrieve(
        dt.date(2021, 1, 1), dt.date(2021, 2, 28), dimensions=("day",)
    )
    report.to_csv("./test.csv")
    with open("./test.csv", mode="r", encoding="utf-8") as f:
        assert len(f.readlines()) == report.shape[0] + 1

    os.remove("./test.csv")


# Test report types


def test_report_type_basic_user_activity(client):
    try:
        report = client.retrieve(dt.date(2021, 1, 1))
        assert report.type == "Basic user activity"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_basic_user_activity_us(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1), filters={"province": "US-OH"}
        )
        assert report.type == "Basic user activity (US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_time_based_activity(client):
    try:
        report = client.retrieve(dt.date(2021, 1, 1), dimensions=("day",))
        assert report.type == "Time-based activity"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_time_based_activity_us(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day",),
            filters={"province": "US-OH"},
        )
        assert report.type == "Time-based activity (US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_geography_based_activity(client):
    try:
        report = client.retrieve(dt.date(2021, 1, 1), dimensions=("country",))
        assert report.type == "Geography-based activity"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_geography_based_activity_us(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("province",),
            filters={"country": "US"},
        )
        assert report.type == "Geography-based activity (US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_user_activity_by_subscribed_status(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("subscribedStatus",),
        )
        assert report.type == "User activity by subscribed status"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_user_activity_by_subscribed_status_us(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("subscribedStatus",),
            filters={"province": "US-OH"},
        )
        assert report.type == "User activity by subscribed status (US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_time_based_playback_details_live(client):
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


def test_report_type_time_based_playback_details_view_percentage(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("youtubeProduct",),
        )
        assert report.type == "Time-based playback details (view percentage)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_geography_based_playback_details_live(client):
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


def test_report_type_geography_based_playback_details_view_percentage(client):
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


def test_report_type_geography_based_playback_details_live_us(client):
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


def test_report_type_geography_based_playback_details_view_percentage_us(
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


def test_report_type_playback_locations(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightPlaybackLocationType",),
        )
        assert report.type == "Playback locations"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_playback_locations_detailed(client):
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


def test_report_type_traffic_sources(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightTrafficSourceType",),
        )
        assert report.type == "Traffic sources"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_traffic_sources_detailed(client):
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


def test_report_type_device_types(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("deviceType",),
        )
        assert report.type == "Device types"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_operating_systems(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("operatingSystem",),
        )
        assert report.type == "Operating systems"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_device_types_and_operating_systems(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("deviceType", "operatingSystem"),
        )
        assert report.type == "Device types and operating systems"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_viewer_demographics(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("ageGroup",),
        )
        assert report.type == "Viewer demographics"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_engagement_and_content_sharing(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1), dimensions=("sharingService",)
        )
        assert report.type == "Engagement and content sharing"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_audience_retention(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("elapsedVideoTimeRatio",),
            filters={"video": "jsQ3TUDcmos"},
        )
        assert report.type == "Audience retention"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_top_videos_by_region(client):
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


def test_report_type_top_videos_by_state(client):
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


def test_report_type_top_videos_by_subscription_status(client):
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


def test_report_type_top_videos_by_youtube_product(client):
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


def test_report_type_top_videos_by_playback_detail(client):
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


def test_report_type_basic_user_activity_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1), filters={"isCurated": "1"}
        )
        assert report.type == "Basic user activity for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_time_based_activity_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Time-based activity for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_geography_based_activity_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("country",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Geography-based activity for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_geography_based_activity_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("province",),
            filters={"isCurated": "1", "country": "US"},
        )
        assert report.type == "Geography-based activity for playlists (US)"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_playback_locations_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightPlaybackLocationType",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Playback locations for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_playback_locations_for_playlists_detailed(client):
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


def test_report_type_traffic_sources_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("insightTrafficSourceType",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Traffic sources for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_traffic_sources_for_playlists_detailed(client):
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


def test_report_type_device_types_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("deviceType",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Device types for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_operating_systems_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("operatingSystem",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Operating systems for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_device_types_and_operating_systems_for_playlists(client):
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


def test_report_type_viewer_demographics_for_playlists(client):
    try:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("ageGroup",),
            filters={"isCurated": "1"},
        )
        assert report.type == "Viewer demographics for playlists"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"


def test_report_type_top_playlists(client):
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


def test_report_type_ad_performance(client):
    try:
        report = client.retrieve(dt.date(2021, 1, 1), dimensions=("adType",))
        assert report.type == "Ad performance"
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{inspect.stack()[0][3]} report raised: {exc}"
