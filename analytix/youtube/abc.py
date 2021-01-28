import abc
import datetime as dt

import pandas as pd

from analytix import InvalidRequest, NoAuthorisedService


class YouTubeAnalyticsReport:
    __slots__ = ("data", "ncolumns", "nrows")

    def __init__(self, data):
        self.data = data
        self.ncolumns = len(data["columnHeaders"])
        self.nrows = len(data["rows"])

    def to_dataframe(self):
        df = pd.DataFrame()
        df = df.append(self.data["rows"])
        df.columns = [c["name"] for c in self.data["columnHeaders"]]
        return df

    def to_json(self, file, indent=4):
        if not file.endswith(".json"):
            file += ".json"
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=indent, ensure_ascii=False)

    def to_csv(self, file):
        if not file.endswith(".csv"):
            file += ".csv"
        self.to_dataframe().to_csv(file)


class YouTubeAnalytics(metaclass=abc.ABCMeta):
    __slots__ = ("service", "metrics", "dimensions", "filters")

    def __init__(self, service):
        self.service = service

    def _check_features(self, report, metrics, dimensions, filters):
        raise NotImplementedError("you need to use a class that inherits from this one")

    def retrieve(self, metrics, start_date, **kwargs):
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
