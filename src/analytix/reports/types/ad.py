# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

__all__ = ("AdPerformance",)

from analytix.abc import ReportType
from analytix.reports.features import Dimensions
from analytix.reports.features import Filters
from analytix.reports.features import Metrics
from analytix.reports.features import Optional
from analytix.reports.features import Required
from analytix.reports.features import SortOptions
from analytix.reports.features import ZeroOrOne


class AdPerformance(ReportType):
    def __init__(self) -> None:
        self.name = "Ad performance"
        self.dimensions = Dimensions(Required("adType"), Optional("day"))
        self.filters = Filters(
            ZeroOrOne("video", "group"),
            ZeroOrOne("country", "continent", "subContinent"),
        )
        self.metrics = Metrics("grossRevenue", "adImpressions", "cpm")
        self.sort_options = SortOptions(*self.metrics.values)
