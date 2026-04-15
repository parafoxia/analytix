# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

from analytix.reports.constraints import OneOrMore
from analytix.reports.constraints import Optional
from analytix.reports.constraints import Required
from analytix.reports.constraints import ZeroOrOne
from analytix.reports.parameters import Dimensions
from analytix.reports.parameters import Filters
from analytix.reports.parameters import Metrics

from . import ReportType


class AdPerformance(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Ad performance",
            metrics=Metrics(OneOrMore("grossRevenue", "adImpressions", "cpm")),
            dimensions=Dimensions(Required("adType"), Optional("day")),
            filters=Filters(
                ZeroOrOne("video", "group"),
                ZeroOrOne("country", "continent", "subContinent"),
            ),
        )
