# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

from analytix.reports import types as rt

# AD PERFORMANCE


def test_ad_performance_1():
    report = rt.AdPerformance()
    assert report.name == "Ad performance"
    d = ["adType", "day"]
    f = {"video": "nf97ng98bg9", "country": "US"}
    m = ["grossRevenue", "adImpressions", "cpm"]
    s = ["grossRevenue", "adImpressions", "cpm"]
    report.validate(d, f, m, s)


def test_ad_performance_2():
    report = rt.AdPerformance()
    assert report.name == "Ad performance"
    d = ["adType"]
    f = {"group": "nf97ng98bg9", "continent": "002"}
    m = ["grossRevenue", "adImpressions", "cpm"]
    s = ["grossRevenue", "adImpressions", "cpm"]
    report.validate(d, f, m, s)


def test_ad_performance_3():
    report = rt.AdPerformance()
    assert report.name == "Ad performance"
    d = ["adType"]
    f = {"subContinent": "014"}
    m = ["grossRevenue", "adImpressions", "cpm"]
    s = ["grossRevenue", "adImpressions", "cpm"]
    report.validate(d, f, m, s)


def test_ad_performance_4():
    report = rt.AdPerformance()
    assert report.name == "Ad performance"
    d = ["adType"]
    f = {}
    m = ["grossRevenue", "adImpressions", "cpm"]
    s = ["grossRevenue", "adImpressions", "cpm"]
    report.validate(d, f, m, s)
