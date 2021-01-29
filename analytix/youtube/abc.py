import abc
import datetime as dt

import pandas as pd

from analytix import InvalidRequest, NoAuthorisedService


class YouTubeAnalyticsReport:
    """An ABC for YouTube Analytics reports. This ABC is not inherited within analytix.

    Args:
        data (dict): The response data from the YouTube Analytics API.

    Attributes:
        data (dict): The response data from the YouTube Analytics API.
        ncolumns (int): The number of columns in the report.
        nrows (int): The number of rows in the report.
    """

    __slots__ = ("data", "ncolumns", "nrows")

    def __init__(self, data):
        self.data = data
        self.ncolumns = len(data["columnHeaders"])
        self.nrows = len(data["rows"])

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
            indent (int): The number of spaces to use for indentation.
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


class YouTubeAnalytics(metaclass=abc.ABCMeta):
    """An ABC from which YouTube analytics classes inherit.

    Args:
        service (YouTubeService): The YouTube service to perform the operation on.

    Attributes:
        service (YouTubeService): The YouTube service to perform the operation on.
    """

    __slots__ = ("service",)

    def __init__(self, service):
        self.service = service

    def _check_features(self, report, metrics, dimensions, filters):
        raise NotImplementedError("you need to use a class that inherits from this one")

    def retrieve(self, metrics, start_date, **kwargs):
        """Executes an API request to pull down analytical information.

        Args:
            metrics (tuple[str, ...] | list[str]): The YouTube Analytics metrics to use, such as views, likes, and comments.
            start_date (datetime.date): The start date for fetching YouTube Analytics data.
            end_date (datetime.date): The end date for fetching YouTube Analytics data. Defaults to the current date, but if the monetary scope is enabled, a few days of data may be missing.
            currency (str): The currency to use for monetary analytics in ISO 4217 format. Defaults to USD.
            dimensions (tuple[str, ...] | list[str]): The YouTube Analytics dimensions, such as video, ageGroup, or gender. Defaults to an empty tuple.
            filters (dict[str, str]): A list of filters that should be applied when retrieving YouTube Analytics data. When providing multiple values for the same filter, separate them with commas. Defaults to an empty dict.
            include_historical_data (bool): Indicates whether the API response should include channels' watch time and view data from the time period prior to when the channels were linked to the content owner. The day and month dimensions overwrite this option. Defaults to False.
            max_results (int | None): The maximum number of rows to include in the response. Defaults to None.
            sort_by (tuple[str, ...] | list[str]): A series of dimensions in which to sort the data. The first dimension is how the data will be sorted at first, followed by the second, and so forth. Defaults to an empty tuple, though data is typically automatically sorted by the YouTube Analytics API.
            sort_descending (bool): Whether to sort in descending order. Defaults to False.
            start_index (int): The index of the first entity to retrieve. Note that this is one-indexed, **not** zero-indexed. Defaults to 1.

        Returns:
            YouTubeAnalyticsReport: The report object containing the data fetched by the YouTube Analytics API.

        Raises:
            InvalidRequest: The request was invalid.
        """
        if not self.service._service:
            raise NoAuthorisedService("the YouTube service has not been authorised")

        end_date = kwargs.get("end_date", dt.date.today())
        currency = kwargs.get("currency", "USD")
        dimensions = kwargs.get("dimensions", ())
        filters = kwargs.get("filters", {})
        include_historical_data = kwargs.get("include_historical_data", False)
        max_results = kwargs.get("max_results", False)
        sort_by = kwargs.get("sort_by", ())
        sort_descending = kwargs.get("sort_descending", False)
        start_index = kwargs.get("start_index", 1)

        self._check_features(metrics, dimensions, filters)
        if filters:
            filters = tuple(f"{k}=={v}" for k, v in filters.items())

        return YouTubeAnalyticsReport(
            self.service._service.reports()
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
            .execute()
        )


class Features(metaclass=abc.ABCMeta):
    __slots__ = ("none", "req", "opt", "many")

    def __init__(self, none=False, req=[], opt=[], many=[]):
        self.none = none
        self.req = [set(x) for x in req]
        self.opt = [set(x) for x in opt]
        self.many = [set(x) for x in many]

    @property
    def every(self):
        e = []
        for x in [*[*self.req], *[*self.opt], *[*self.many]]:
            e.extend(x)
        return e

    def verify(self, against):
        raise NotImplementedError()
