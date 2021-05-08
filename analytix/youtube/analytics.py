import datetime as dt
import logging

from analytix.errors import (
    Deprecated,
    InvalidRequest,
    NoAuthorisedService,
)

from . import api
from .api.iso import CURRENCIES
from .reports import AnalyticsReport


class Analytics:
    __slots__ = ("service",)

    def __init__(self, service):
        self.service = service

    def retrieve(self, metrics="all", playlist=False, **kwargs):
        # NOTE: Requests only valid after July 1 2008?

        start_date = kwargs.pop(
            "start_date", dt.date.today() - dt.timedelta(days=28)
        )
        end_date = kwargs.pop("end_date", dt.date.today())
        currency = kwargs.pop("currency", "USD")
        dimensions = kwargs.pop("dimensions", ())
        filters = kwargs.pop("filters", {})
        include_historical_data = kwargs.pop("include_historical_data", False)
        max_results = kwargs.pop("max_results", None)
        sort_by = kwargs.pop("sort_by", ())
        start_index = kwargs.pop("start_index", 1)

        if playlist:
            filters.update({"isCurated": "1"})
            logging.debug("Filters updated to use playlists")

        if kwargs:
            raise InvalidRequest(
                f"one or more kwargs you provided are invalid ({', '.join(kwargs.keys())})"
            )

        if "7DayTotals" in dimensions or "30DayTotals" in dimensions:
            raise Deprecated(
                "the '7DayTotals' and '30DayTotals' dimensions were deprecated, and can no longer be used"
            )

        if not isinstance(start_date, dt.date):
            raise InvalidRequest(
                f"expected start date as date object, got {type(start_date).__name__}"
            )

        if not isinstance(end_date, dt.date):
            raise InvalidRequest(
                f"expected end date as date object, got {type(end_date).__name__}"
            )

        if end_date <= start_date:
            raise InvalidRequest(
                f"the start date should be earlier than the end date"
            )

        if currency not in CURRENCIES:
            raise InvalidRequest(
                f"expected currency as ISO 4217 alpha-3 code, got {currency}"
            )

        if not isinstance(dimensions, (tuple, list, set)):
            raise InvalidRequest(
                f"expected tuple, list, or set of dimensions, got {type(dimensions).__name__}"
            )

        if not isinstance(filters, dict):
            raise InvalidRequest(
                f"expected dict of filters, got {type(filters).__name__}"
            )

        r = api.reports.determine(metrics, dimensions, filters)()
        logging.info(f"Report type determined as: {r}")

        if metrics == "all":
            metrics = tuple(r.metrics)
        elif not isinstance(metrics, (tuple, list, set)):
            raise InvalidRequest(
                f"expected tuple, list, or set of metrics, got {type(metrics).__name__}"
            )
        logging.debug("Using these metrics: " + ", ".join(metrics))

        r.verify(dimensions, metrics, filters)
        logging.debug("Verification complete")

        if filters:
            filters = tuple(f"{k}=={v}" for k, v in filters.items())

        if not self.service.authorised:
            self.service.authorise()

        logging.info("Retrieving YouTube analytics data...")
        return AnalyticsReport(
            self.service.authorised.reports()
            .query(
                ids="channel==MINE",
                metrics=",".join(metrics),
                startDate=start_date,
                endDate=end_date,
                currency=currency,
                dimensions=",".join(dimensions),
                filters=";".join(filters),
                includeHistoricalChannelData=include_historical_data,
                maxResults=max_results,
                sort=",".join(sort_by),
                startIndex=start_index,
            )
            .execute(),
            r,
        )
