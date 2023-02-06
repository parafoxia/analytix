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

import pytest

from analytix.errors import InvalidRequest
from analytix.reports import data
from analytix.reports import types as rt


def test_str_output():
    report = rt.BasicUserActivity()
    assert str(report) == "Basic user activity"


def test_detailed_report_no_max_results():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "insightPlaybackLocationType": "EMBEDDED",
        "country": "US",
        "video": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    with pytest.raises(InvalidRequest) as exc:
        report.validate(d, f, m, s, 0)
    assert str(exc.value) == "expected a maximum number of results"


def test_detailed_report_too_high_max_results():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "insightPlaybackLocationType": "EMBEDDED",
        "country": "US",
        "video": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    with pytest.raises(InvalidRequest) as exc:
        report.validate(d, f, m, s, 100)
    assert str(exc.value) == "expected no more than 25 results, got 100"


def test_detailed_report_start_index_too_high():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "insightPlaybackLocationType": "EMBEDDED",
        "country": "US",
        "video": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]
    with pytest.raises(InvalidRequest) as exc:
        report.validate(d, f, m, s, 25, 20)
    assert str(exc.value) == "the start index is too high"


def test_detailed_report_no_sort_options():
    report = rt.PlaybackLocationDetail()
    assert report.name == "Playback locations (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "insightPlaybackLocationType": "EMBEDDED",
        "country": "US",
        "video": "fn849bng984b",
        "liveOrOnDemand": "LIVE",
    }
    m = data.LOCATION_AND_TRAFFIC_METRICS
    with pytest.raises(InvalidRequest) as exc:
        report.validate(d, f, m, [], 25)
    assert str(exc.value) == "expected at least 1 sort option, got 0"
