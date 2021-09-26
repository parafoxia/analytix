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
