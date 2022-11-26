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

# BASIC USER ACTIVITY


def test_basic_user_activity_playlist_1():
    report = rt.BasicUserActivityPlaylist()
    assert report.name == "Basic user activity for playlists"
    d = []
    f = {
        "isCurated": "1",
        "country": "US",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_basic_user_activity_playlist_2():
    report = rt.BasicUserActivityPlaylist()
    assert report.name == "Basic user activity for playlists"
    d = []
    f = {
        "isCurated": "1",
        "province": "US-OH",
        "group": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_basic_user_activity_playlist_3():
    report = rt.BasicUserActivityPlaylist()
    assert report.name == "Basic user activity for playlists"
    d = []
    f = {"isCurated": "1", "continent": "002"}
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_basic_user_activity_playlist_4():
    report = rt.BasicUserActivityPlaylist()
    assert report.name == "Basic user activity for playlists"
    d = []
    f = {"isCurated": "1", "subContinent": "014"}
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_basic_user_activity_playlist_5():
    report = rt.BasicUserActivityPlaylist()
    assert report.name == "Basic user activity for playlists"
    d = []
    f = {"isCurated": "1"}
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


# TIME-BASED ACTIVITY


def test_time_based_activity_playlist_1():
    report = rt.TimeBasedActivityPlaylist()
    assert report.name == "Time-based activity for playlists"
    d = ["day", "subscribedStatus"]
    f = {
        "isCurated": "1",
        "country": "US",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_time_based_activity_playlist_2():
    report = rt.TimeBasedActivityPlaylist()
    assert report.name == "Time-based activity for playlists"
    d = ["month", "subscribedStatus", "youtubeProduct"]
    f = {
        "isCurated": "1",
        "province": "US-OH",
        "group": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_time_based_activity_playlist_3():
    report = rt.TimeBasedActivityPlaylist()
    assert report.name == "Time-based activity for playlists"
    d = ["day"]
    f = {"isCurated": "1", "continent": "002"}
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_time_based_activity_playlist_4():
    report = rt.TimeBasedActivityPlaylist()
    assert report.name == "Time-based activity for playlists"
    d = ["month"]
    f = {"isCurated": "1", "subContinent": "014"}
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_time_based_activity_playlist_5():
    report = rt.TimeBasedActivityPlaylist()
    assert report.name == "Time-based activity for playlists"
    d = ["day"]
    f = {"isCurated": "1"}
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


# GEOGRAPHY-BASED ACTIVITY


def test_geography_based_activity_playlist_1():
    report = rt.GeographyBasedActivityPlaylist()
    assert report.name == "Geography-based activity for playlists"
    d = ["country", "subscribedStatus"]
    f = {
        "isCurated": "1",
        "continent": "002",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_geography_based_activity_playlist_2():
    report = rt.GeographyBasedActivityPlaylist()
    assert report.name == "Geography-based activity for playlists"
    d = ["country", "subscribedStatus", "youtubeProduct"]
    f = {
        "isCurated": "1",
        "subContinent": "014",
        "group": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_geography_based_activity_playlist_3():
    report = rt.GeographyBasedActivityPlaylist()
    assert report.name == "Geography-based activity for playlists"
    d = ["country"]
    f = {"isCurated": "1"}
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


# GEOGRAPHY-BASED ACTIVITY (US)


def test_geography_based_activity_us_playlist_1():
    report = rt.GeographyBasedActivityUSPlaylist()
    assert report.name == "Geography-based activity for playlists (US)"
    d = ["province", "subscribedStatus"]
    f = {
        "isCurated": "1",
        "country": "US",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_geography_based_activity_us_playlist_2():
    report = rt.GeographyBasedActivityUSPlaylist()
    assert report.name == "Geography-based activity for playlists (US)"
    d = ["province", "subscribedStatus", "youtubeProduct"]
    f = {
        "isCurated": "1",
        "country": "US",
        "group": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_geography_based_activity_us_playlist_3():
    report = rt.GeographyBasedActivityUSPlaylist()
    assert report.name == "Geography-based activity for playlists (US)"
    d = ["province"]
    f = {"isCurated": "1", "country": "US"}
    m = data.ALL_PLAYLIST_METRICS
    s = data.ALL_PLAYLIST_METRICS
    report.validate(d, f, m, s)


# PLAYBACK LOCATIONS


def test_playback_location_playlist_1():
    report = rt.PlaybackLocationPlaylist()
    assert report.name == "Playback locations for playlists"
    d = ["insightPlaybackLocationType", "day"]
    f = {
        "isCurated": "1",
        "country": "US",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_playback_location_playlist_2():
    report = rt.PlaybackLocationPlaylist()
    assert report.name == "Playback locations for playlists"
    d = ["insightPlaybackLocationType", "day", "subscribedStatus"]
    f = {"isCurated": "1", "province": "US-OH", "group": "nf97ng98bg9"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_playback_location_playlist_3():
    report = rt.PlaybackLocationPlaylist()
    assert report.name == "Playback locations for playlists"
    d = ["insightPlaybackLocationType"]
    f = {"isCurated": "1", "continent": "002"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_playback_location_playlist_4():
    report = rt.PlaybackLocationPlaylist()
    assert report.name == "Playback locations for playlists"
    d = ["insightPlaybackLocationType"]
    f = {"isCurated": "1", "subContinent": "014"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_playback_location_playlist_5():
    report = rt.PlaybackLocationPlaylist()
    assert report.name == "Playback locations for playlists"
    d = ["insightPlaybackLocationType"]
    f = {"isCurated": "1"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


# PLAYBACK LOCATIONS (DETAILED)


def test_playback_location_detail_playlist_1():
    report = rt.PlaybackLocationDetailPlaylist()
    assert report.name == "Playback locations for playlists (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "isCurated": "1",
        "insightPlaybackLocationType": "EMBEDDED",
        "country": "US",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_playback_location_detail_playlist_2():
    report = rt.PlaybackLocationDetailPlaylist()
    assert report.name == "Playback locations for playlists (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "isCurated": "1",
        "insightPlaybackLocationType": "EMBEDDED",
        "province": "US-OH",
        "group": "nf97ng98bg9",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_playback_location_detail_playlist_3():
    report = rt.PlaybackLocationDetailPlaylist()
    assert report.name == "Playback locations for playlists (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "isCurated": "1",
        "insightPlaybackLocationType": "EMBEDDED",
        "continent": "002",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_playback_location_detail_playlist_4():
    report = rt.PlaybackLocationDetailPlaylist()
    assert report.name == "Playback locations for playlists (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "isCurated": "1",
        "insightPlaybackLocationType": "EMBEDDED",
        "subContinent": "014",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_playback_location_detail_playlist_5():
    report = rt.PlaybackLocationDetailPlaylist()
    assert report.name == "Playback locations for playlists (detailed)"
    d = ["insightPlaybackLocationDetail"]
    f = {
        "isCurated": "1",
        "insightPlaybackLocationType": "EMBEDDED",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


# TRAFFIC SOURCES


def test_traffic_source_playlist_1():
    report = rt.TrafficSourcePlaylist()
    assert report.name == "Traffic sources for playlists"
    d = ["insightTrafficSourceType", "day"]
    f = {
        "isCurated": "1",
        "country": "US",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_traffic_source_playlist_2():
    report = rt.TrafficSourcePlaylist()
    assert report.name == "Traffic sources for playlists"
    d = ["insightTrafficSourceType", "day", "subscribedStatus"]
    f = {"isCurated": "1", "province": "US-OH", "group": "nf97ng98bg9"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_traffic_source_playlist_3():
    report = rt.TrafficSourcePlaylist()
    assert report.name == "Traffic sources for playlists"
    d = ["insightTrafficSourceType"]
    f = {"isCurated": "1", "continent": "002"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_traffic_source_playlist_4():
    report = rt.TrafficSourcePlaylist()
    assert report.name == "Traffic sources for playlists"
    d = ["insightTrafficSourceType"]
    f = {"isCurated": "1", "subContinent": "014"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_traffic_source_playlist_5():
    report = rt.TrafficSourcePlaylist()
    assert report.name == "Traffic sources for playlists"
    d = ["insightTrafficSourceType"]
    f = {"isCurated": "1"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


# TRAFFIC SOURCES (DETAILED)


def test_traffic_source_detail_playlist_1():
    report = rt.TrafficSourceDetailPlaylist()
    assert report.name == "Traffic sources for playlists (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {
        "isCurated": "1",
        "insightTrafficSourceType": "ADVERTISING",
        "country": "US",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_traffic_source_detail_playlist_2():
    report = rt.TrafficSourceDetailPlaylist()
    assert report.name == "Traffic sources for playlists (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {
        "isCurated": "1",
        "insightTrafficSourceType": "ADVERTISING",
        "province": "US-OH",
        "group": "nf97ng98bg9",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_traffic_source_detail_playlist_3():
    report = rt.TrafficSourceDetailPlaylist()
    assert report.name == "Traffic sources for playlists (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {
        "isCurated": "1",
        "insightTrafficSourceType": "ADVERTISING",
        "continent": "002",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_traffic_source_detail_playlist_4():
    report = rt.TrafficSourceDetailPlaylist()
    assert report.name == "Traffic sources for playlists (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {
        "isCurated": "1",
        "insightTrafficSourceType": "ADVERTISING",
        "subContinent": "014",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_traffic_source_detail_playlist_5():
    report = rt.TrafficSourceDetailPlaylist()
    assert report.name == "Traffic sources for playlists (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {
        "isCurated": "1",
        "insightTrafficSourceType": "ADVERTISING",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS]
    report.validate(d, f, m, s, 25)


def test_traffic_source_detail_playlist_invalid_source():
    report = rt.TrafficSourceDetailPlaylist()
    assert report.name == "Traffic sources for playlists (detailed)"
    d = ["insightTrafficSourceDetail"]
    f = {"isCurated": "1", "insightTrafficSourceType": "ANNOTATION"}
    m = data.LOCATION_AND_TRAFFIC_METRICS
    s = [f"-{o}" for o in data.LOCATION_AND_TRAFFIC_SORT_OPTIONS]

    with pytest.raises(
        InvalidRequest,
        match="dimensions and filters are incompatible with value 'ANNOTATION' for filter 'insightTrafficSourceType'",
    ):
        report.validate(d, f, m, s, 25)


# DEVICE TYPES


def test_device_type_playlist_1():
    report = rt.DeviceTypePlaylist()
    assert report.name == "Device types for playlists"
    d = ["deviceType", "day"]
    f = {
        "isCurated": "1",
        "country": "US",
        "playlist": "nf97ng98bg9",
        "operatingSystem": "WINDOWS",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_device_type_playlist_2():
    report = rt.DeviceTypePlaylist()
    assert report.name == "Device types for playlists"
    d = ["deviceType", "day", "subscribedStatus"]
    f = {
        "isCurated": "1",
        "province": "US-OH",
        "group": "nf97ng98bg9",
        "operatingSystem": "WINDOWS",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_device_type_playlist_3():
    report = rt.DeviceTypePlaylist()
    assert report.name == "Device types for playlists"
    d = ["deviceType", "day", "subscribedStatus", "youtubeProduct"]
    f = {
        "isCurated": "1",
        "continent": "002",
        "operatingSystem": "WINDOWS",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_device_type_playlist_4():
    report = rt.DeviceTypePlaylist()
    assert report.name == "Device types for playlists"
    d = ["deviceType"]
    f = {"isCurated": "1", "subContinent": "014"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_device_type_playlist_5():
    report = rt.DeviceTypePlaylist()
    assert report.name == "Device types for playlists"
    d = ["deviceType"]
    f = {"isCurated": "1"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


# OPERATING SYSTEMS


def test_operating_system_playlist_1():
    report = rt.OperatingSystemPlaylist()
    assert report.name == "Operating systems for playlists"
    d = ["operatingSystem", "day"]
    f = {
        "isCurated": "1",
        "country": "US",
        "playlist": "nf97ng98bg9",
        "deviceType": "MOBILE",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_operating_system_playlist_2():
    report = rt.OperatingSystemPlaylist()
    assert report.name == "Operating systems for playlists"
    d = ["operatingSystem", "day", "subscribedStatus"]
    f = {
        "isCurated": "1",
        "province": "US-OH",
        "group": "nf97ng98bg9",
        "deviceType": "MOBILE",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_operating_system_playlist_3():
    report = rt.OperatingSystemPlaylist()
    assert report.name == "Operating systems for playlists"
    d = ["operatingSystem", "day", "subscribedStatus", "youtubeProduct"]
    f = {
        "isCurated": "1",
        "continent": "002",
        "deviceType": "MOBILE",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_operating_system_playlist_4():
    report = rt.OperatingSystemPlaylist()
    assert report.name == "Operating systems for playlists"
    d = ["operatingSystem"]
    f = {"isCurated": "1", "subContinent": "014"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_operating_system_playlist_5():
    report = rt.OperatingSystemPlaylist()
    assert report.name == "Operating systems for playlists"
    d = ["operatingSystem"]
    f = {"isCurated": "1"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


# DEVICE TYPES AND OPERATING SYSTEMS


def test_device_type_and_operating_system_playlist_1():
    report = rt.DeviceTypeAndOperatingSystemPlaylist()
    assert report.name == "Device types and operating systems for playlists"
    d = ["deviceType", "operatingSystem", "day"]
    f = {
        "isCurated": "1",
        "country": "US",
        "playlist": "nf97ng98bg9",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_device_type_and_operating_system_playlist_2():
    report = rt.DeviceTypeAndOperatingSystemPlaylist()
    assert report.name == "Device types and operating systems for playlists"
    d = ["deviceType", "operatingSystem", "day", "subscribedStatus"]
    f = {
        "isCurated": "1",
        "province": "US-OH",
        "group": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_device_type_and_operating_system_playlist_3():
    report = rt.DeviceTypeAndOperatingSystemPlaylist()
    assert report.name == "Device types and operating systems for playlists"
    d = ["deviceType", "operatingSystem", "day", "subscribedStatus", "youtubeProduct"]
    f = {
        "isCurated": "1",
        "continent": "002",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_device_type_and_operating_system_playlist_4():
    report = rt.DeviceTypeAndOperatingSystemPlaylist()
    assert report.name == "Device types and operating systems for playlists"
    d = ["deviceType", "operatingSystem"]
    f = {"isCurated": "1", "subContinent": "014"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


def test_device_type_and_operating_system_playlist_5():
    report = rt.DeviceTypeAndOperatingSystemPlaylist()
    assert report.name == "Device types and operating systems for playlists"
    d = ["deviceType", "operatingSystem"]
    f = {"isCurated": "1"}
    m = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    s = data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
    report.validate(d, f, m, s)


# VIEWER DEMOGRAPHICS


def test_viewer_demographics_playlist_1():
    report = rt.ViewerDemographicsPlaylist()
    assert report.name == "Viewer demographics for playlists"
    d = ["ageGroup", "subscribedStatus"]
    f = {
        "isCurated": "1",
        "country": "US",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = ["viewerPercentage"]
    s = ["viewerPercentage"]
    report.validate(d, f, m, s)


def test_viewer_demographics_playlist_2():
    report = rt.ViewerDemographicsPlaylist()
    assert report.name == "Viewer demographics for playlists"
    d = ["ageGroup", "gender"]
    f = {
        "isCurated": "1",
        "province": "US-OH",
        "group": "nf97ng98bg9",
    }
    m = ["viewerPercentage"]
    s = ["viewerPercentage"]
    report.validate(d, f, m, s)


def test_viewer_demographics_playlist_3():
    report = rt.ViewerDemographicsPlaylist()
    assert report.name == "Viewer demographics for playlists"
    d = ["gender"]
    f = {"isCurated": "1", "continent": "002"}
    m = ["viewerPercentage"]
    s = ["viewerPercentage"]
    report.validate(d, f, m, s)


def test_viewer_demographics_playlist_4():
    report = rt.ViewerDemographicsPlaylist()
    assert report.name == "Viewer demographics for playlists"
    d = ["gender"]
    f = {"isCurated": "1", "subContinent": "014"}
    m = ["viewerPercentage"]
    s = ["viewerPercentage"]
    report.validate(d, f, m, s)


def test_viewer_demographics_playlist_5():
    report = rt.ViewerDemographicsPlaylist()
    assert report.name == "Viewer demographics for playlists"
    d = ["gender"]
    f = {"isCurated": "1"}
    m = ["viewerPercentage"]
    s = ["viewerPercentage"]
    report.validate(d, f, m, s)


# TOP PLAYLISTS


def test_top_playlists_1():
    report = rt.TopPlaylists()
    assert report.name == "Top playlists"
    d = ["playlist"]
    f = {
        "isCurated": "1",
        "country": "US",
        "playlist": "nf97ng98bg9",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_playlists_2():
    report = rt.TopPlaylists()
    assert report.name == "Top playlists"
    d = ["playlist"]
    f = {
        "isCurated": "1",
        "province": "US-OH",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_playlists_3():
    report = rt.TopPlaylists()
    assert report.name == "Top playlists"
    d = ["playlist"]
    f = {
        "isCurated": "1",
        "continent": "002",
        "playlist": "nf97ng98bg9",
        "subscribedStatus": "SUBSCRIBED",
        "youtubeProduct": "CORE",
    }
    m = data.ALL_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_playlists_4():
    report = rt.TopPlaylists()
    assert report.name == "Top playlists"
    d = ["playlist"]
    f = {"isCurated": "1", "subContinent": "014"}
    m = data.ALL_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)


def test_top_playlists_5():
    report = rt.TopPlaylists()
    assert report.name == "Top playlists"
    d = ["playlist"]
    f = {"isCurated": "1"}
    m = data.ALL_PLAYLIST_METRICS
    s = [f"-{o}" for o in data.TOP_VIDEOS_SORT_OPTIONS]
    report.validate(d, f, m, s, 200)
