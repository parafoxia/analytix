import datetime as dt
import json
import os

import pytest  # type: ignore

from analytix import YouTubeAnalytics
from analytix.errors import *


@pytest.fixture()
def client():
    client = YouTubeAnalytics.from_file("./secrets/secrets.json")
    client.authorise()
    return client


def test_client(client):
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


def test_reports_sort(client):
    import numpy as np

    report = client.retrieve(
        dt.date(2021, 1, 1),
        dt.date(2021, 2, 28),
        dimensions=("day",),
        sort_by=("views",),
    )
    assert np.array_equal(report.rows[:, 1], np.sort(report.rows[:, 1]))


def test_reports_verify(client):
    # TODO: Add input verification tests
    # Deprecated
    with pytest.raises(Deprecated) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1), dimensions=("7DayTotals",)
        )

    # Start date
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve("2020/1/1", dimensions=("day",))
    assert str(exc.value).startswith("expected start date as date object")

    # End date
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), "2020/1/1")
    assert str(exc.value).startswith("expected end date as date object")

    # End date > start date
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), dt.date(2019, 1, 1))
    assert str(exc.value).startswith(
        "the start date should be earlier than the end date"
    )

    # End date = start date
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), dt.date(2020, 1, 1))
    assert str(exc.value).startswith(
        "the start date should be earlier than the end date"
    )

    # Invalid currency
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), currency="ZZZ")
    assert str(exc.value).startswith(
        "expected existing currency as ISO 4217 alpha-3 code"
    )

    # Non-iterable dimension
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), dimensions="day")
    assert str(exc.value).startswith(
        "expected tuple, list, or set of dimensions"
    )

    # Non-dict filters
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), filters="country==US")
    assert str(exc.value).startswith("expected dict of filters")

    # Non-bool historical
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2020, 1, 1), include_historical_data=1
        )
    assert str(exc.value).startswith(
        "expected bool for 'include_historical_data'"
    )

    # Non-int max results
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), max_results="5")
    assert str(exc.value).startswith("expected int for 'max_results'")

    # Start index too low
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), max_results=-1)
    assert str(exc.value).startswith(
        "the maximum number of results should be no less than 0 (0 for unlimited results)"
    )

    # Non-iterable sort
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2020, 1, 1), dimensions=("day",), sort_by="views"
        )
    assert str(exc.value).startswith(
        "expected tuple, list, or set of sorting columns"
    )

    # Non-int start index
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), start_index="5")
    assert str(exc.value).startswith("expected int for 'start_index'")

    # Start index too low
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2020, 1, 1), start_index=0)
    assert str(exc.value).startswith(
        "the start index should be no less than 1"
    )

    # Non-iterable metrics
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2020, 1, 1), dimensions=("day",), metrics="views"
        )
    assert str(exc.value).startswith("expected tuple, list, or set of metrics")

    # Invalid dimension
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(dt.date(2021, 1, 1), dimensions=("test",))
    assert str(exc.value).startswith(
        "one or more dimensions you provided are invalid"
    )

    # Unsupported dimension
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1), dimensions=("day", "country")
        )
    assert str(exc.value).startswith(
        "one or more dimensions you provided are not supported by the selected report type"
    )

    # Invalid filter
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day",),
            filters={"test": "invalid"},
        )
    assert str(exc.value).startswith(
        "one or more filters you provided are invalid"
    )

    # Unsupported filter
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("country",),
            filters={"province": "US-OH"},
        )
    assert str(exc.value).startswith(
        "one or more filters you provided are not supported by the selected report type"
    )

    # Invalid filter value
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("day",),
            filters={"province": "US-XX"},
        )
    assert "is not a valid value for filter" in str(exc.value)

    # Invalid metric
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

    # Unsupported metric
    with pytest.raises(InvalidRequest) as exc:
        report = client.retrieve(
            dt.date(2021, 1, 1),
            dimensions=("subscribedStatus",),
            metrics=("views", "likes", "comments"),
        )
    assert str(exc.value).startswith(
        "one or more metrics you provided are not supported by the selected report type"
    )

    # Required dimension
    # Required filter
    # Exactly one dimension
    # Exactly one filter
    # One or more dimension
    # One or more filter
    # Optional dimension
    # Optional filter
    # Zero or one dimension
    # Zero or one filter


def test_report_types(client):
    try:
        type = "Basic user activity"
        report = client.retrieve(dt.date(2021, 1, 1))
        assert report.type == type
        type = "Basic user activity (US)"
        report = client.retrieve(
            dt.date(2021, 1, 1), filters={"province": "US-OH"}
        )
        assert report.type == type
    except (InvalidRequest, HTTPError) as exc:
        assert False, f"{type} report raised: {exc}"


def test_dataframe_datetime(client):
    import numpy as np
    import pandas as pd

    report = client.retrieve(
        dt.date(2021, 1, 1), dt.date(2021, 2, 28), dimensions=("day",)
    )
    df = report.to_dataframe()
    assert df.shape == (59, 36)
    assert pd.api.types.is_datetime64_ns_dtype(df["day"])

    report = client.retrieve(
        dt.date(2021, 1, 1), dt.date(2021, 2, 1), dimensions=("month",)
    )
    df = report.to_dataframe()
    assert df.shape == (2, 36)
    assert pd.api.types.is_datetime64_ns_dtype(df["month"])


def test_files_csv(client):
    report = client.retrieve(
        dt.date(2021, 1, 1), dt.date(2021, 2, 28), dimensions=("day",)
    )
    report.to_csv("./test.csv")
    with open("./test.csv", mode="r", encoding="utf-8") as f:
        assert len(f.readlines()) == 60

    os.remove("./test.csv")
