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

import pytest  # type: ignore

from analytix import YouTubeAnalytics
from analytix.errors import InvalidRequest


@pytest.fixture()
def client():
    client = YouTubeAnalytics.from_file("./secrets/secrets.json")
    client.authorise()
    return client


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
