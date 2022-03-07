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

from __future__ import annotations

import datetime as dt
import logging
import typing as t

import analytix
from analytix import data
from analytix import report_types as rt
from analytix.abc import ReportType
from analytix.errors import InvalidRequest

log = logging.getLogger(__name__)


class Query:
    __slots__ = (
        "dimensions",
        "filters",
        "metrics",
        "sort_options",
        "max_results",
        "_start_date",
        "_end_date",
        "currency",
        "start_index",
        "_include_historical_data",
        "rtype",
    )

    def __init__(
        self,
        dimensions: t.Collection[str] | None = None,
        filters: dict[str, str] | None = None,
        metrics: t.Collection[str] | None = None,
        sort_options: t.Collection[str] | None = None,
        max_results: int = 0,
        start_date: dt.date | None = None,
        end_date: dt.date | None = None,
        currency: str = "USD",
        start_index: int = 1,
        include_historical_data: bool = False,
    ) -> None:
        self.dimensions = dimensions or ()
        self.filters = filters or {}
        self.metrics = metrics or ()
        self.sort_options = sort_options or ()
        self.max_results = max_results

        self._end_date = end_date or dt.date.today()
        self._start_date = start_date or (self._end_date - dt.timedelta(days=28))
        self.currency = currency
        self.start_index = start_index
        self._include_historical_data = include_historical_data

        self.rtype: ReportType | None = None

    @property
    def start_date(self) -> str:
        return self._start_date.strftime("%Y-%m-%d")

    @property
    def end_date(self) -> str:
        return self._end_date.strftime("%Y-%m-%d")

    @property
    def include_historical_data(self) -> str:
        return f"{self._include_historical_data}".lower()

    @property
    def url(self) -> str:
        filters = ";".join(f"{k}=={v}" for k, v in self.filters.items())
        return analytix.API_BASE_URL + (
            "ids=channel==MINE"
            f"&dimensions={','.join(self.dimensions)}"
            f"&filters={filters}"
            f"&metrics={','.join(self.metrics)}"
            f"&sort={','.join(self.sort_options)}"
            f"&maxResults={self.max_results}"
            f"&startDate={self.start_date}"
            f"&endDate={self.end_date}"
            f"&currency={self.currency}"
            f"&startIndex={self.start_index}"
            f"&includeHistoricalData={self.include_historical_data}"
        )

    def validate(self) -> None:
        log.info("Validating request...")

        if self.max_results < 0:
            raise InvalidRequest(
                "the max results should be non-negative (0 for unlimited results)"
            )

        if not isinstance(self._start_date, dt.date):
            raise InvalidRequest("expected start date as date object")

        if not isinstance(self._end_date, dt.date):
            raise InvalidRequest("expected end date as date object")

        if self._end_date < self._start_date:
            raise InvalidRequest("the start date should be earlier than the end date")

        log.info(f"Getting data between {self.start_date} and {self.end_date}")

        if self.currency not in data.CURRENCIES:
            raise InvalidRequest("expected a valid ISO 4217 currency")

        if self.start_index < 1:
            raise InvalidRequest("the start index should be positive")

        if "month" in self.dimensions:
            if self._start_date.day != 1 or self._end_date.day != 1:
                log.warning(
                    "Correcting start and end dates -- if 'month' is passed as a "
                    "dimension, the day should always be 1"
                )
                self._start_date = dt.date(
                    self._start_date.year, self._start_date.month, 1
                )
                self._end_date = dt.date(self._end_date.year, self._end_date.month, 1)

        self.rtype = rt.determine(self.dimensions, self.filters, self.metrics)
        log.info(f"Report type determined as {self.rtype.name!r}")

        if not self.metrics:
            self.metrics = [
                m for m in data.ALL_METRICS if m in self.rtype.metrics.values
            ]
            log.debug("Metrics set to: " + ", ".join(self.metrics))

        self.rtype.validate(
            self.dimensions,
            self.filters,
            self.metrics,
            self.sort_options,
            self.max_results,
        )

        # If it gets to this point, it's fine.
        log.info("Request OK!")