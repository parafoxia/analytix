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
from analytix.queries import Query


def test_create_defaults():
    query = Query()
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
    query = Query(
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
async def query() -> Query:
    return Query(
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
    assert query.url == analytix.API_BASE_URL + (
            "ids=channel==MINE"
            f"&dimensions=day,country"
            f"&filters=continent==002;deviceType==MOBILE"
            f"&metrics=views,likes,comments"
            f"&sort=shares,dislikes"
            f"&maxResults=0"
            f"&startDate=2021-01-01"
            f"&endDate=2021-12-31"
            f"&currency=USD"
            f"&startIndex=1"
            f"&includeHistoricalData=false"
        )


def test_validate_max_results():
    query = Query(max_results=-1)
    with pytest.raises(InvalidRequest) as exc:
        query.validate()
    assert str(exc.value) == "the max results should be non-negative (0 for unlimited results)"


def test_validate_start_date_is_date():
    query = Query(start_date="2021-01-01")
    with pytest.raises(InvalidRequest) as exc:
        query.validate()
    assert str(exc.value) == "expected start date as date object"


def test_validate_end_date_is_date():
    query = Query(end_date="2021-01-01", start_date=dt.date(2021, 1, 1))
    with pytest.raises(InvalidRequest) as exc:
        query.validate()
    assert str(exc.value) == "expected end date as date object"


def test_validate_end_date_gt_start_date():
    query = Query(end_date=dt.date(2021, 1, 1), start_date=dt.date(2021, 1, 2))
    with pytest.raises(InvalidRequest) as exc:
        query.validate()
    assert str(exc.value) == "the start date should be earlier than the end date"


def test_validate_currency():
    query = Query(currency="LOL")
    with pytest.raises(InvalidRequest) as exc:
        query.validate()
    assert str(exc.value) == "expected a valid ISO 4217 currency code"


def test_validate_start_index():
    query = Query(start_index=0)
    with pytest.raises(InvalidRequest) as exc:
        query.validate()
    assert str(exc.value) == "the start index should be positive"


def test_validate_months_are_corrected():
    query = Query(dimensions=["month"], start_date=dt.date(2021, 4, 2), end_date=dt.date(2022, 3, 31))
    query.validate()
    assert query._start_date == dt.date(2021, 4, 1)
    assert query._end_date == dt.date(2022, 3, 1)
