import datetime as dt
import json

import pandas as pd

from analytix import InvalidRequest, NoAuthorisedService
from analytix.youtube import features, reports


class YouTubeAnalyticsReport:
    """A class that provides an interface for working with data retrieved from the YouTube Analytics API.

    Args:
        data (dict): The response data from the YouTube Analytics API.
        type_ (ReportType): The type of report generated.

    Attributes:
        data (dict): The response data from the YouTube Analytics API.
        ncolumns (int): The number of columns in the report.
        nrows (int): The number of rows in the report.
        type (ReportType): The type of report generated.
    """

    __slots__ = ("data", "ncolumns", "nrows", "type")

    def __init__(self, data, type_):
        self.data = data
        self.ncolumns = len(data["columnHeaders"])
        self.nrows = len(data["rows"])
        self.type = type_

    def to_dataframe(self):
        """Returns the report as a Pandas DataFrame.

        Returns:
            pandas.DataFrame: The DataFrame object.
        """
        df = pd.DataFrame()
        df = df.append(self.data["rows"])
        df.columns = [c["name"] for c in self.data["columnHeaders"]]
        return df

    def to_json(self, file, indent=4):
        """Exports the report to a JSON file in the same format as it was provided by the YouTube Analytics API.

        Args:
            file (str | os.PathLike): The path in which the report should be saved.
            indent (int): The number of spaces to use for indentation. Defaults to 4.
        """
        if not file.endswith(".json"):
            file += ".json"
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=indent, ensure_ascii=False)

    def to_csv(self, file):
        """Exports the report to a CSV file.

        Args:
            file (str | os.PathLike): The path in which the report should be saved.
        """
        if not file.endswith(".csv"):
            file += ".csv"
        self.to_dataframe().to_csv(file)

    def __str__(self):
        return self.type


class YouTubeAnalytics:
    """A class to retrieve data from the YouTube Analytics API.

    Args:
        service (YouTubeService): The YouTube service to perform the operation on.

    Attributes:
        service (YouTubeService): The YouTube service to perform the operation on.
    """

    __slots__ = ("service",)

    def __init__(self, service):
        self.service = service

    def get_report_type(self, metrics=(), dimensions=(), filters={}, *, verify=True):
        """Gets the report type that best matches the metrics, dimensions, and filters given. If :code:`verify` is False, this will return a :code:`Generic` report type.

        Args:
            metrics (tuple[str, ...] | list[str]): The metrics (or columns) to retrieve. Defaults to an empty tuple.
            dimensions (tuple[str, ...] | list[str]): The dimensions in which data is split. Defaults to an empty tuple.
            filters (dict[str, str]): The filters to be applied when retrieving data. Defaults to an empty dictionary.
            verify (bool): Whether to attempt to determine the report type dynamically. Defaults to True.

        Returns:
            ReportType: The selected report type.
        """
        if not verify:
            return reports.Generic()
        return reports.determine(metrics, dimensions, filters)()

    def get_verified_report_type(self, metrics=(), dimensions=(), filters={}):
        """Like :code:`get_report_type`, but only returns a ReportType object if verification succeeds.

        Args:
            metrics (tuple[str, ...] | list[str]): The metrics (or columns) to retrieve. Defaults to an empty tuple.
            dimensions (tuple[str, ...] | list[str]): The dimensions in which data is split. Defaults to an empty tuple.
            filters (dict[str, str]): The filters to be applied when retrieving data. Defaults to an empty dictionary.

        Returns:
            ReportType | InvalidRequest: The selected report type or the error that caused verification to fail.
        """
        r = self.get_report_type(metrics, dimensions, filters)
        try:
            r.verify(metrics, dimensions, filters, 5, ("views",))
            return r
        except InvalidRequest as exc:
            return exc

    def retrieve(self, metrics="all", verify=True, **kwargs):
        """Executes an API request to pull down analytical information.

        .. warning::

            The :code:`start_date` and :code:`end_date` parameters do not account for delayed analytics such as revenue.

        .. note::

            This will retrieve video reports by default. To retrieve playlist reports, include '"isCurated": "1"' in your filters.

        Args:
            metrics (tuple[str, ...] | list[str]): The metrics (or columns) to retrieve. Defaults to "all".
            verify (bool): Whether to verify the requests before passing them to the API. Defaults to True.
            start_date (datetime.date): The earliest date to fetch data for. Defaults to 28 days before the current date.
            end_date (datetime.date): The latest date to fetch data for. Defaults to the current date.
            currency (str): The currency to use for monetary analytics. This should be passed in ISO 4217 format. Defaults to USD.
            dimensions (tuple[str, ...] | list[str]): The dimensions in which data is split. Defaults to an empty tuple.
            filters (dict[str, str]): The filters to be applied when retrieving data. Defaults to an empty dictionary.
            include_historical_data (bool): Whether data before the point in which the specified channel(s) were linked to the content owner should be retrieved. Defaults to False.
            max_results (int | None): The maximum number of rows to fetch. Defaults to None.
            sort_by (tuple[str, ...] | list[str]): The dimensions in which to sort the data. Defaults to an empty tuple.
            start_index (int): The index of the first row to retrieve. Note that this is one-indexed. Defaults to 1.

        Returns:
            YouTubeAnalyticsReport: The report object containing the data fetched from the YouTube Analytics API.

        Raises:
            NoAuthorisedService: The given service has not been authorised.
            InvalidRequest: The request was invalid.
        """
        if not self.service.active:
            raise NoAuthorisedService("the YouTube service has not been authorised")

        start_date = kwargs.get("start_date", dt.date.today() - dt.timedelta(days=28))
        end_date = kwargs.get("end_date", dt.date.today())
        currency = kwargs.get("currency", "USD")
        dimensions = kwargs.get("dimensions", ())
        filters = kwargs.get("filters", {})
        include_historical_data = kwargs.get("include_historical_data", False)
        max_results = kwargs.get("max_results", None)
        sort_by = kwargs.get("sort_by", ())
        start_index = kwargs.get("start_index", 1)

        if not isinstance(dimensions, (tuple, list, set)):
            raise InvalidRequest(f"expected tuple, list, or set of dimensions, got {type(dimensions).__name__}")

        if not isinstance(filters, dict):
            raise InvalidRequest(f"expected dict of filters, got {type(filters).__name__}")

        r = self.get_report_type(metrics, dimensions, filters, verify=verify)
        r.verify(metrics, dimensions, filters, max_results, sort_by)

        if metrics == "all":
            if not verify:
                raise InvalidRequest("you must manually specify a list of metrics when not verifying")
            metrics = r.metrics

        if filters:
            filters = tuple(f"{k}=={v}" for k, v in filters.items())

        return YouTubeAnalyticsReport(
            self.service.active.reports()
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
