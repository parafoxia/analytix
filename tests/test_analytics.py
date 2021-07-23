import datetime as dt
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


def test_client_project_id_match(client):
    with open("./secrets/secrets.json", mode="r", encoding="utf-8") as f:
        project_id = json.load(f)["installed"]["project_id"]
    assert client.project_id == project_id


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
    import numpy as np

    report = client.retrieve(
        dt.date(2021, 1, 1),
        dt.date(2021, 2, 28),
        dimensions=("day",),
        sort_by=("views",),
    )
    arr = [r[1] for r in report.data["rows"]]
    assert arr == sorted(arr)


def test_reports_sort_descending(client):
    import numpy as np

    report = client.retrieve(
        dt.date(2021, 1, 1),
        dt.date(2021, 2, 28),
        dimensions=("day",),
        sort_by=("-views",),
    )
    arr = [r[1] for r in report.data["rows"]]
    assert arr == sorted(arr, reverse=True)


# Input verification


def test_reports_verify_check_deprecated(client):
    with pytest.raises(Deprecated) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1), dimensions=("7DayTotals",)
        )
    assert (
        str(exc.value)
        == "the '7DayTotals' and '30DayTotals' dimensions were deprecated, and can no longer be used"
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
        "expected existing currency as ISO 4217 alpha-3 code"
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
        "the maximum number of results should be no less than 0 (0 for unlimited results)"
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


# Report verification


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
        "one or more dimensions you provided are not supported by the selected report type"
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
        "one or more filters you provided are not supported by the selected report type"
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
        "one or more metrics you provided are not supported by the selected report type"
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


# def test_report_type_basic_user_activity(client):
#     try:
#         report = client.retrieve(dt.date(2021, 1, 1))
#         assert report.type == "Basic user activity"
#     except (InvalidRequest, HTTPError) as exc:
#         assert False, f"{type} report raised: {exc}"


# def test_report_type_basic_user_activity_us(client):
#     try:
#         report = client.retrieve(
#             dt.date(2021, 1, 1), filters={"province": "US-OH"}
#         )
#         assert report.type == "Basic user activity (US)"
#     except (InvalidRequest, HTTPError) as exc:
#         assert False, f"{type} report raised: {exc}"


# Time-based activity
# Time-based activity (US)
# Geography-based activity
# Geography-based activity (US)
# User activity by subscribed status
# User activity by subscribed status (US)
# Time-based playback details (live)
# Time-based playback details (view percentage)
# Geography-based playback details (live)
# Geography-based playback details (view percentage)
# Geography-based playback details (live, US)
# Geography-based playback details (view percentage, US)
# Playback locations
# Playback locations (detailed)
# Traffic sources
# Traffic sources (detailed)
# Device types
# Operating systems
# Device types and operating systems
# Viewer demographics
# Engagement and content sharing
# def test_report_type_engagement_and_content_sharing(client):
#     try:
#         report = client.retrieve(
#             dt.date(2021, 1, 1), dimensions=("sharingService",)
#         )
#         assert report.type == "Engagement and content sharing"
#     except (InvalidRequest, HTTPError) as exc:
#         assert False, f"{type} report raised: {exc}"
# Audience retention
# def test_report_type_audience_retention(client):
#     try:
#         report = client.retrieve(
#             dt.date(2021, 1, 1), dimensions=("elapsedVideoTimeRatio",)
#         )
#         assert report.type == "Audience retention"
#     except (InvalidRequest, HTTPError) as exc:
#         assert False, f"{type} report raised: {exc}"
# Top videos by region
# Top videos by state
# Top videos by subscription status
# Top videos by YouTube product
# Top videos by playback detail
