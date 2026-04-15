# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import datetime as dt
import json
import logging
import warnings
from collections.abc import Collection
from typing import NoReturn

from analytix.auth import Scopes
from analytix.constants import API_REPORTS_URL
from analytix.errors import InputValidationError
from analytix.errors import ParameterError
from analytix.errors import ValidationError
from analytix.errors import ValidationExceptionGroup
from analytix.mixins import RequestMixin
from analytix.session import Session
from analytix.warnings import InvalidMonthFormatWarning

from .constants import ALL_DIMENSIONS
from .constants import ALL_FILTERS
from .constants import ALL_METRICS
from .constants import ALL_METRICS_ORDERED
from .constants import CURRENCIES
from .constants import REVENUE_METRICS
from .interfaces import Report
from .types import ReportType
from .types.ad import AdPerformance
from .types.playlist import BasicUserActivityPlaylist
from .types.playlist import DeviceTypeAndOperatingSystemPlaylist
from .types.playlist import DeviceTypePlaylist
from .types.playlist import GeographyBasedActivityPlaylist
from .types.playlist import GeographyBasedActivityUSPlaylist
from .types.playlist import OperatingSystemPlaylist
from .types.playlist import PlaybackLocationDetailPlaylist
from .types.playlist import PlaybackLocationPlaylist
from .types.playlist import TimeBasedActivityPlaylist
from .types.playlist import TopPlaylists
from .types.playlist import TrafficSourceDetailPlaylist
from .types.playlist import TrafficSourcePlaylist
from .types.playlist import ViewerDemographicsPlaylist
from .types.video import AudienceRetention
from .types.video import BasicUserActivity
from .types.video import BasicUserActivityUS
from .types.video import DeviceType
from .types.video import DeviceTypeAndOperatingSystem
from .types.video import EngagementAndContentSharing
from .types.video import GeographyBasedActivity
from .types.video import GeographyBasedActivityByCity
from .types.video import GeographyBasedActivityUS
from .types.video import OperatingSystem
from .types.video import PlaybackDetailsLiveGeographyBased
from .types.video import PlaybackDetailsLiveGeographyBasedUS
from .types.video import PlaybackDetailsLiveTimeBased
from .types.video import PlaybackDetailsSubscribedStatus
from .types.video import PlaybackDetailsSubscribedStatusUS
from .types.video import PlaybackDetailsViewPercentageGeographyBased
from .types.video import PlaybackDetailsViewPercentageGeographyBasedUS
from .types.video import PlaybackDetailsViewPercentageTimeBased
from .types.video import PlaybackLocation
from .types.video import PlaybackLocationDetail
from .types.video import TimeBasedActivity
from .types.video import TimeBasedActivityUS
from .types.video import TopVideosPlaybackDetail
from .types.video import TopVideosRegional
from .types.video import TopVideosSubscribed
from .types.video import TopVideosUS
from .types.video import TopVideosYouTubeProduct
from .types.video import TrafficSource
from .types.video import TrafficSourceDetail
from .types.video import ViewerDemographics

REPORT_TYPES = [
    BasicUserActivity,
    BasicUserActivityUS,
    TimeBasedActivity,
    TimeBasedActivityUS,
    GeographyBasedActivity,
    GeographyBasedActivityUS,
    GeographyBasedActivityByCity,
    PlaybackDetailsSubscribedStatus,
    PlaybackDetailsSubscribedStatusUS,
    PlaybackDetailsLiveTimeBased,
    PlaybackDetailsViewPercentageTimeBased,
    PlaybackDetailsLiveGeographyBased,
    PlaybackDetailsViewPercentageGeographyBased,
    PlaybackDetailsLiveGeographyBasedUS,
    PlaybackDetailsViewPercentageGeographyBasedUS,
    PlaybackLocation,
    PlaybackLocationDetail,
    TrafficSource,
    TrafficSourceDetail,
    DeviceType,
    OperatingSystem,
    DeviceTypeAndOperatingSystem,
    ViewerDemographics,
    EngagementAndContentSharing,
    AudienceRetention,
    TopVideosRegional,
    TopVideosUS,
    TopVideosSubscribed,
    TopVideosYouTubeProduct,
    TopVideosPlaybackDetail,
    BasicUserActivityPlaylist,
    TimeBasedActivityPlaylist,
    GeographyBasedActivityPlaylist,
    GeographyBasedActivityUSPlaylist,
    PlaybackLocationPlaylist,
    PlaybackLocationDetailPlaylist,
    TrafficSourcePlaylist,
    TrafficSourceDetailPlaylist,
    DeviceTypePlaylist,
    OperatingSystemPlaylist,
    DeviceTypeAndOperatingSystemPlaylist,
    ViewerDemographicsPlaylist,
    TopPlaylists,
    AdPerformance,
]

_log = logging.getLogger(__name__)


class ReportBuilder(RequestMixin):
    def __init__(
        self,
        *,
        dimensions: Collection[str] | None = None,
        filters: dict[str, str] | None = None,
        metrics: Collection[str] | None = None,
        sort_options: Collection[str] | None = None,
        max_results: int = 0,
        start_date: dt.date | None = None,
        end_date: dt.date | None = None,
        currency: str = "USD",
        start_index: int = 1,
        include_historical_data: bool = False,
        display_nested_exceptions: bool = False,
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

        self._display_nested_exceptions = display_nested_exceptions

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
        return API_REPORTS_URL + (
            "?ids=channel==MINE"
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

    def _validate_inputs(self) -> None:
        _log.debug("Validating inputs")
        errors = []

        if diff := set(self.dimensions) - ALL_DIMENSIONS:
            errors.append(
                ParameterError(
                    f"invalid dimensions provided: {', '.join(diff)}",
                ),
            )

        if diff := set(self.filters) - ALL_FILTERS:
            errors.append(
                ParameterError(f"invalid filters provided: {', '.join(diff)}"),
            )

        if diff := set(self.metrics) - ALL_METRICS:
            errors.append(
                ParameterError(f"invalid metrics provided: {', '.join(diff)}"),
            )

        if diff := {o.lstrip("-") for o in self.sort_options} - ALL_METRICS:
            errors.append(
                ParameterError(
                    f"invalid sort options provided: {', '.join(diff)}",
                ),
            )

        if self.max_results < 0:
            errors.append(
                InputValidationError(
                    "expected a non-negative integer for max results "
                    f"(or 0 for unlimited results), got {self.max_results}",
                ),
            )

        if not isinstance(self._start_date, dt.date):
            errors.append(
                InputValidationError(
                    "expected a date object for start date, got ",
                    f"{type(self._start_date).__name__}",
                ),
            )

        if not isinstance(self._end_date, dt.date):
            errors.append(
                InputValidationError(
                    "expected a date object for end date, got ",
                    f"{type(self._end_date).__name__}",
                ),
            )

        if self._start_date > self._end_date:
            errors.append(
                InputValidationError(
                    "expected the start date to be before the end date",
                ),
            )

        if self.currency not in CURRENCIES:
            errors.append(
                InputValidationError(
                    "expected a valid ISO 4217 currency code, got ",
                    f"{self.currency}",
                ),
            )

        if self.start_index < 1:
            errors.append(
                InputValidationError(
                    "expected a positive integer for start index, got ",
                    f"{self.start_index}",
                ),
            )

        if errors:
            raise ValidationExceptionGroup("input errors found", errors)

        if "month" in self.dimensions and (
            self._start_date.day != 1 or self._end_date.day != 1
        ):
            warnings.warn(
                "Correcting start and end dates -- if 'month' is passed as a "
                "dimension, these should always be the first day of the month",
                InvalidMonthFormatWarning,
                stacklevel=2,
            )
            self._start_date = dt.date(self._start_date.year, self._start_date.month, 1)
            self._end_date = dt.date(self._end_date.year, self._end_date.month, 1)

        _log.debug("No input validation errors found!")
        _log.debug("Getting data between %s and %s", self.start_date, self.end_date)

    def _set_metrics(self, report_type: ReportType, scopes: Scopes) -> None:
        if not self.metrics:
            self.metrics = [
                m for m in ALL_METRICS_ORDERED if m in report_type.metrics.all_keys
            ]

        if not scopes & Scopes.MONETARY_READONLY:
            self.metrics = [m for m in self.metrics if m not in REVENUE_METRICS]
        elif not scopes & Scopes.READONLY:
            self.metrics = [m for m in self.metrics if m in REVENUE_METRICS]

        _log.debug("Metrics set to: " + ", ".join(self.metrics))

    def _handle_single_error(
        self,
        errors: dict[ReportType, list[ValidationError]],
    ) -> ReportType:
        best_type = max(
            errors.keys(),
            key=lambda rt: (
                -len(errors[rt]),
                sum(e.value for e in errors[rt]),
                len(rt.metrics.all_keys),
            ),
        )

        if len(errors[best_type]):
            err = ValidationExceptionGroup(
                "unable to find a suitable report type",
                errors[best_type],
            )
            err.add_note(f"Best candidate: {best_type.name}")
            raise err

    def _handle_multiple_errors(
        self,
        errors: dict[ReportType, list[ValidationError]],
    ) -> NoReturn:
        min_errors = min(len(v) for v in errors.values())
        best_errors = {k: v for k, v in errors.items() if len(v) == min_errors}
        err = ValidationExceptionGroup(
            "unable to find any suitable report types",
            [
                ValidationExceptionGroup(rt.name, type_errors)
                for rt, type_errors in best_errors.items()
            ],
        )
        err.add_note(
            "The best candidates are: " + ", ".join(rt.name for rt in best_errors),
        )
        raise err

    def _validate_report_type(self, report_type: ReportType) -> None:
        _log.debug("Validating report type: %s", report_type.name)
        errors = report_type.validate(
            input_dimensions=self.dimensions,
            input_filters=self.filters,
            input_metrics=self.metrics,
            input_sort_options=self.sort_options,
            max_results=self.max_results,
            start_index=self.start_index,
        )

        if errors:
            raise ValidationExceptionGroup(
                f"invalid parameters for selected report type: {report_type.name}",
                errors,
            )

    def _validate_parameters(self) -> ReportType:
        _log.debug("Validating report parameters")
        errors: dict[ReportType, list[ValidationError]] = {}

        for rt_cls in REPORT_TYPES:
            rt = rt_cls()
            errors[rt] = rt.validate(
                input_dimensions=self.dimensions,
                input_filters=self.filters,
                input_metrics=self.metrics,
                input_sort_options=self.sort_options,
                max_results=self.max_results,
                start_index=self.start_index,
            )

        if _log.isEnabledFor(logging.DEBUG):
            _log.debug(
                "Found %s error(s) across %s report types: %s",
                sum(len(type_errors) for type_errors in errors.values()),
                len(REPORT_TYPES),
                " | ".join(
                    f"{rt.name!r} ({len(type_errors)}e, "
                    f"{sum(e.value for e in type_errors)}v)"
                    for rt, type_errors in errors.items()
                    if type_errors
                ),
            )

        suitable_types = [rt for rt, type_errors in errors.items() if not type_errors]

        if not suitable_types:
            if self._display_nested_exceptions:
                self._handle_multiple_errors(errors)
            else:
                self._handle_single_error(errors)

        _log.debug(
            "Found %s suitable report types: %s",
            len(suitable_types),
            ", ".join(rt.name for rt in suitable_types),
        )
        _log.debug("Selecting report type with most metrics")
        selected = max(suitable_types, key=lambda rt: len(rt.metrics.all_keys))
        _log.debug("Selected report type: %s", selected.name)
        return selected

    def build(
        self,
        *,
        report_type_cls: type[ReportType] | None = None,
        session: Session,
    ) -> Report:
        self._validate_inputs()
        if report_type_cls:
            self._validate_report_type(report_type := report_type_cls())
        else:
            report_type = self._validate_parameters()
        self._set_metrics(report_type, session.scopes)

        with self._request(self.url, token=session.access_token) as resp:
            data = json.loads(resp.data)

        report = Report(data)
        _log.info("Created '%s' report of shape %s", report_type.name, report.shape)
        return report
