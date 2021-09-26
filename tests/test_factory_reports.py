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


@pytest.fixture()
def client():
    client = YouTubeAnalytics.from_file("./secrets/secrets.json")
    client.authorise()
    return client


def test_daily_analytics_rows_correct(client):
    report = client.daily_analytics()
    assert report.type == "Time-based activity"
    assert report.shape[0] == 28 or report.shape[0] == 29
    report = client.daily_analytics(last=10)
    assert report.type == "Time-based activity"
    assert report.shape[0] == 10 or report.shape[0] == 11


def test_daily_analytics_start_date(client):
    report = client.daily_analytics(since=dt.date(2021, 1, 1))
    assert report.type == "Time-based activity"
    assert report.data["rows"][0][0] == "2021-01-01"


def test_daily_analytics_metrics(client):
    report = client.daily_analytics(metrics=("views", "likes", "comments"))
    assert report.type == "Time-based activity"
    assert report.shape[1] == 4


def test_monthly_analytics_rows_correct(client):
    report = client.monthly_analytics()
    assert report.type == "Time-based activity"
    assert report.shape[0] == 3
    report = client.monthly_analytics(last=10)
    assert report.type == "Time-based activity"
    assert report.shape[0] == 10


def test_monthly_analytics_start_date(client):
    report = client.monthly_analytics(since=dt.date(2021, 1, 1))
    assert report.type == "Time-based activity"
    assert report.data["rows"][0][0] == "2021-01"
    report = client.monthly_analytics(since=dt.date(2020, 6, 12))
    assert report.type == "Time-based activity"
    assert report.data["rows"][0][0] == "2020-06"


def test_monthly_analytics_end_date(client):
    report = client.monthly_analytics(since=dt.date(2021, 1, 1))
    assert report.type == "Time-based activity"
    last_month = dt.date.today() - dt.timedelta(days=30)
    assert report.data["rows"][-1][0] == dt.date(
        last_month.year, last_month.month, 1
    ).strftime("%Y-%m")


def test_monthly_analytics_metrics(client):
    report = client.monthly_analytics(metrics=("views", "likes", "comments"))
    assert report.type == "Time-based activity"
    assert report.shape[1] == 4


def test_regional_analytics_metrics_sorted(client):
    report = client.regional_analytics()
    assert report.type == "Geography-based activity"
    arr = [r[1] for r in report.data["rows"]]
    assert arr == sorted(arr, reverse=True)


def test_regional_analytics_metrics(client):
    report = client.regional_analytics(metrics=("views", "likes", "comments"))
    assert report.type == "Geography-based activity"
    assert report.shape[1] == 4


def test_top_videos_metrics_sorted(client):
    report = client.top_videos()
    assert report.type == "Top videos by region"
    arr = [r[1] for r in report.data["rows"]]
    assert arr == sorted(arr, reverse=True)


def test_top_videos_metrics(client):
    report = client.top_videos(metrics=("views", "likes", "comments"))
    assert report.type == "Top videos by region"
    assert report.shape[1] == 4
