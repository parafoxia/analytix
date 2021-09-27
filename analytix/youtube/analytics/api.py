# Copyright (c) 2021, Ethan Henderson
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

import datetime as dt
import json
import logging
import os
import time

import requests
from requests_oauthlib import OAuth2Session

from analytix.errors import (
    HTTPError,
    InvalidRequest,
    InvalidScopes,
    MissingOptionalComponents,
)
from analytix.iso import CURRENCIES
from analytix.packages import PANDAS_AVAILABLE
from analytix.secrets import TOKEN_STORE, YT_ANALYTICS_TOKEN
from analytix.youtube.analytics import (
    YOUTUBE_ANALYTICS_API_VERSION,
    YOUTUBE_ANALYTICS_SCOPES,
    verify,
)

if PANDAS_AVAILABLE:
    import pandas as pd

log = logging.getLogger("analytix")


class YouTubeAnalytics:
    """A client class to retrieve data from the YouTube Analytics API.
    This should only be created from the relevant class methods.

    Args:
        session (OAuth2Session): The OAuth 2 session to use.
        secrets (dict[str, str]): A dictionary containing Google
            Developers project secrets. This is not expected in the same
            format as the Google Developers console provides it.

    Attributes:
        secrets (dict[str, str]): A dictionary containing Google
            Developers project secrets.
        project_id (str): The ID of the Google Developers project.
    """

    __slots__ = ("_session", "secrets", "project_id", "_token")

    def __init__(self, session, secrets):
        self._session = session
        self.secrets = secrets
        self.project_id = secrets["project_id"]
        self._token = self._get_token()

    def __str__(self):
        return self.project_id

    def __repr__(self):
        return f"<YouTubeAnalytics project_id={self.project_id!r}>"

    @property
    def authorised(self):
        """Whether the project is authorised.

        Returns:
            bool
        """
        return bool(self._token)

    authorized = authorised

    @classmethod
    def from_file(cls, path, *, scopes="all", **kwargs):
        """Creates the client object using a secrets file.

        Args:
            path (str): The path to the secrets file.

        Keyword Args:
            scopes (iterable[str] | str): The scopes to use. Defaults to
                "all".
            **kwargs (Any): Additional arguments to pass to the
                OAuth2Session constructor.

        Returns:
            YouTubeAnalytics: A ready-to-use client object.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(
                "you must provide a valid path to a secrets file"
            )

        with open(path, mode="r", encoding="utf-8") as f:
            log.debug("Secrets file loaded")
            secrets = json.load(f)["installed"]

        scopes = cls._resolve_scopes(scopes)
        session = OAuth2Session(
            secrets["client_id"],
            redirect_uri=secrets["redirect_uris"][0],
            scope=scopes,
            **kwargs,
        )
        return cls(session, secrets)

    @classmethod
    def from_dict(cls, secrets, *, scopes="all", **kwargs):
        """Creates the client object using a secrets dictionary.

        Args:
            secrets (dict[str, dict[str, str]]): The secrets dictionary.

        Keyword Args:
            scopes (iterable[str] | str): The scopes to use. Defaults to
                "all".
            **kwargs (Any): Additional arguments to pass to the
                OAuth2Session constructor.

        Returns:
            YouTubeAnalytics: A ready-to-use client object.
        """
        scopes = cls._resolve_scopes(scopes)
        session = OAuth2Session(
            secrets["installed"]["client_id"],
            redirect_uri=secrets["redirect_uris"][0],
            scope=scopes,
            **kwargs,
        )
        return cls(session, secrets["installed"])

    @staticmethod
    def _resolve_scopes(scopes):
        if scopes == "all":
            log.debug(f"Scopes set to {YOUTUBE_ANALYTICS_SCOPES}")
            return YOUTUBE_ANALYTICS_SCOPES

        if not isinstance(scopes, (tuple, list, set)):
            raise InvalidScopes(
                "expected tuple, list, or set of scopes, "
                f"got {type(scopes).__name__}"
            )

        for i, scope in enumerate(scopes[:]):
            if not scope.startswith("https://www.googleapis.com/auth/"):
                scopes[i] = "https://www.googleapis.com/auth/" + scope

        diff = set(scopes) - set(YOUTUBE_ANALYTICS_SCOPES)
        if diff:
            raise InvalidScopes(
                "one or more scopes you provided are invalid: "
                + ", ".join(diff)
            )

        log.debug(f"Scopes set to {scopes}")
        return scopes

    @staticmethod
    def _get_token():
        if not os.path.isfile(TOKEN_STORE / YT_ANALYTICS_TOKEN):
            log.info("No token found; you will need to authorise")
            return ""

        with open(
            TOKEN_STORE / YT_ANALYTICS_TOKEN, mode="r", encoding="utf-8"
        ) as f:
            data = json.load(f)
        if time.time() > data["expires"]:
            log.info(
                "Token found, but it has expired; you will need to authorise"
            )
            return ""

        log.info(
            (
                "Valid token found; analytix will use this, so you don't need "
                "to authorise"
            )
        )
        return data["token"]

    def authorise(self, store_token=True, force=False, **kwargs):
        """Authorises the client. This is typically called automatically
        when needed, so you often don't need to call this unless you
        want to override the default behaviour.

        Keyword Args:
            store_token (bool): Whether to store the token locally for
                future uses. Note that tokens are only valid for an hour
                before they expire. Defaults to True.
            force (bool): Whether to force an authorisation even when
                authorisation credentials are still valid. If this is
                False, calls to this method won't do anything if the
                client is already authorised. Defaults to False.
            **kwargs (Any): Additional arguments to pass when creating
                the authorisation URL.
        """
        if self._token and not force:
            log.info("Client is already authorised! Skipping...")
            return

        url, _ = self._session.authorization_url(
            self.secrets["auth_uri"], **kwargs
        )
        code = input(f"You need to authorise the session: {url}\nCODE > ")
        token = self._session.fetch_token(
            self.secrets["token_uri"],
            code=code,
            client_secret=self.secrets["client_secret"],
        )
        self._token = token["access_token"]
        log.info("Token retrieved")

        if not store_token:
            log.info("Not storing token, as instructed")
            return

        os.makedirs(TOKEN_STORE, exist_ok=True)
        with open(
            TOKEN_STORE / YT_ANALYTICS_TOKEN, mode="w", encoding="utf-8"
        ) as f:
            json.dump(
                {"token": self._token, "expires": token["expires_at"]},
                f,
                ensure_ascii=False,
            )
            log.info(f"Key stored in {TOKEN_STORE / YT_ANALYTICS_TOKEN}")

    authorize = authorise

    def retrieve(
        self, start_date, end_date=dt.date.today(), metrics="all", **kwargs
    ):
        """Retrieves a report from the YouTube Analytics API.

        Args:
            start_date (datetime.date): The date from which data should
                be collected from.

        Keyword Args:
            end_date (datetime.date): The date to collect data to.
                Defaults to :code:`datetime.date.today()`.
            metrics (iterable[str] | str): The metrics (or columns) to
                use in the report. Defaults to "all".
            dimensions (iterable[str]): The dimensions to use. These
                dimensions are how data is split; for example, if the
                "day" dimension is provided, each row will contain
                information for a different day. Defaults to an empty
                tuple.
            filters (dict[str, str]): The filters to use. To get
                playlist reports, include :code:`"isCurated": "1"`.
                Defaults to an empty dictionary.
            sort_by (iterable[str]): A list of metrics to sort by. To
                sort in descending order, prefix the metric(s) with a
                hyphen (-). Defaults to an empty tuple.
            max_results (int): The maximum number of rows to include in
                the report. Set this to 0 to remove the limit. Defaults
                to 0.
            currency (str): The currency to use in the format defined in
                the `ISO 4217
                <https://www.iso.org/iso-4217-currency-codes.html>`_
                standard. Defaults to "USD".
            start_index (int): The row to start pulling data from. This
                value is one-indexed, meaning the first row is 1, not 0.
                Defaults to 1.
            include_historical_data (bool): Whether to retrieve data
                before the current owner of the channel became
                affiliated with the channel. Defaults to False.

        Returns:
            YouTubeAnalyticsReport: The retrieved report.

        Raises:
            InvalidRequest: Something is wrong with the request.
            HTTPError: The API returned an error.
        """
        dimensions = kwargs.pop("dimensions", ())
        filters = kwargs.pop("filters", {})
        sort_by = kwargs.pop("sort_by", ())
        max_results = kwargs.pop("max_results", 0)
        currency = kwargs.pop("currency", "USD")
        start_index = kwargs.pop("start_index", 1)
        include_historical_data = kwargs.pop("include_historical_data", False)

        log.debug("Verifying options...")
        if "7DayTotals" in dimensions or "30DayTotals" in dimensions:
            raise InvalidRequest(
                "the '7DayTotals' and '30DayTotals' dimensions were "
                "deprecated, and can no longer be used"
            )
        if not isinstance(start_date, dt.date):
            raise InvalidRequest(
                "expected start date as date object, "
                f"got {type(start_date).__name__}"
            )
        if not isinstance(end_date, dt.date):
            raise InvalidRequest(
                "expected end date as date object, "
                f"got {type(end_date).__name__}"
            )
        if end_date <= start_date:
            raise InvalidRequest(
                f"the start date should be earlier than the end date"
            )
        if not isinstance(dimensions, (tuple, list, set)):
            raise InvalidRequest(
                "expected tuple, list, or set of dimensions, "
                f"got {type(dimensions).__name__}"
            )
        if not isinstance(filters, dict):
            raise InvalidRequest(
                f"expected dict of filters, got {type(filters).__name__}"
            )
        if not isinstance(sort_by, (tuple, list, set)):
            raise InvalidRequest(
                "expected tuple, list, or set of sorting columns, "
                f"got {type(sort_by).__name__}"
            )
        if not isinstance(max_results, int):
            raise InvalidRequest(
                "expected int for 'max_results', "
                f"got {type(max_results).__name__}"
            )
        if max_results < 0:
            raise InvalidRequest(
                (
                    "the maximum number of results should be no less than 0 "
                    "(0 for unlimited results)"
                )
            )
        if currency not in CURRENCIES:
            raise InvalidRequest(
                f"expected valid currency as ISO 4217 code, got {currency}"
            )
        if not isinstance(start_index, int):
            raise InvalidRequest(
                (
                    "expected int for 'start_index', "
                    f"got {type(start_index).__name__}"
                )
            )
        if start_index < 1:
            raise InvalidRequest(f"the start index should be no less than 1")
        if not isinstance(include_historical_data, bool):
            raise InvalidRequest(
                "expected bool for 'include_historical_data', "
                f"got {type(include_historical_data).__name__}"
            )

        if "month" in dimensions:
            if start_date.day != 1 or end_date.day != 1:
                log.warning(
                    "The start and end dates must be the first date of the "
                    "month when the 'month' dimension is passed. analytix "
                    "corrects this automatically for convenience, but "
                    "consider manually setting the dates in future to avoid "
                    "undesired results"
                )
                start_date = dt.date(start_date.year, start_date.month, 1)
                end_date = dt.date(end_date.year, end_date.month, 1)

        log.debug("Determining report type...")
        rtype = verify.rtypes.determine(dimensions, metrics, filters)()
        log.info(f"Report type determined as: {rtype}")

        if metrics == "all":
            metrics = tuple(rtype.metrics)
        elif not isinstance(metrics, (tuple, list, set)):
            raise InvalidRequest(
                "expected tuple, list, or set of metrics, "
                f"got {type(metrics).__name__}"
            )
        log.debug("Using these metrics: " + ", ".join(metrics))

        log.debug("Verifying report...")
        rtype.verify(dimensions, metrics, filters, sort_by, max_results)
        log.debug("Verification complete")

        url = (
            "https://youtubeanalytics.googleapis.com/"
            f"{YOUTUBE_ANALYTICS_API_VERSION}/reports"
            "?ids=channel==MINE"
            f"&metrics={','.join(metrics)}"
            f"&startDate={start_date.strftime('%Y-%m-%d')}"
            f"&endDate={end_date.strftime('%Y-%m-%d')}"
            f"&currency={currency}"
            f"&dimensions={','.join(dimensions)}"
            f"&filters={';'.join(f'{k}=={v}' for k, v in filters.items())}"
            "&includeHistorialChannelData="
            f"{f'{include_historical_data}'.lower()}"
            f"&maxResults={max_results}"
            f"&sort={','.join(sort_by)}"
            f"&startIndex={start_index}"
        )
        log.debug(f"URL: {url}")

        if not self._token:
            log.debug("Authorising...")
            self.authorise()

        with requests.get(
            url, headers={"Authorization": f"Bearer {self._token}"}
        ) as r:
            data = r.json()

        if next(iter(data)) == "error":
            error = data["error"]
            raise HTTPError(f"{error['code']}: {error['message']}")

        log.info("Creating report...")
        return YouTubeAnalyticsReport(f"{rtype}", data)

    def daily_analytics(self, of=None, since=None, last=28, metrics="all"):
        """A factory method that retrieves daily video or channel
        analytics.

        .. versionadded:: 2.1

        Keyword Args:
            of (str | None): A video ID. Pass None to include all
                videos. Defaults to None.
            since (datetime.date | None): The date to start collecting
                data from. If this is None, analytix will fall back to
                the :code:`last` kwarg. Defaults to None.
            last (int): The number of days to retrieve data for. If
                :code:`since` is not None, this is ignored. This
                accounts for delayed revenue analytics, but does mean
                that an extra day of data may sometimes be included in
                the report. In this case, that means the report may
                contain either :code:`last` or :code:`last + 1` rows.
                Defaults to 28.
            metrics (iterable[str] | str): A list of metrics to use.
                Defaults to "all".

        Returns:
            YouTubeAnalyticsReport: The retrieved report.

        Raises:
            InvalidRequest: Something is wrong with the request.
            HTTPError: The API returned an error.
        """
        return self.retrieve(
            since or dt.date.today() - dt.timedelta(days=last + 2),
            dimensions=("day",),
            metrics=metrics,
            filters={"video": of} if of else {},
        )

    def monthly_analytics(self, of=None, since=None, last=3, metrics="all"):
        """A factory method that retrieves monthly video or channel
        analytics.

        .. versionadded:: 2.1

        Keyword Args:
            of (str | None): A video ID. Pass None to include all
                videos. Defaults to None.
            since (datetime.date | None): The date to start collecting
                data from. If this is None, analytix will fall back to
                the :code:`last` kwarg. The :code:`day` argument for the
                date constructor must be set to 1 -- if it is not, it
                will be set to 1 for you. Defaults to None.
            last (int): The number of months to retrieve data for. If
                :code:`since` is not None, this is ignored. The current
                month is not included in reports retrieved using this
                method. The number passed here will be the number of
                rows in the report. Defaults to 3.
            metrics (iterable[str] | str): A list of metrics to use.
                Defaults to "all".

        Returns:
            YouTubeAnalyticsReport: The retrieved report.

        Raises:
            InvalidRequest: Something is wrong with the request.
            HTTPError: The API returned an error.
        """

        def _resolve_date(original):
            return dt.date(original.year, original.month, 1)

        return self.retrieve(
            _resolve_date(
                since or dt.date.today() - dt.timedelta(days=last * 31)
            ),
            _resolve_date(dt.date.today() - dt.timedelta(days=31)),
            dimensions=("month",),
            metrics=metrics,
            filters={"video": of} if of else {},
        )

    def regional_analytics(self, since=None, last=28, metrics="all"):
        """A factory method that retrieves channel analytics by country.
        This is automatically sorted by views.

        .. versionadded:: 2.1

        Keyword Args:
            since (datetime.date | None): The date to start collecting
                data from. If this is None, analytix will fall back to
                the :code:`last` kwarg. Defaults to None.
            last (int): The number of days to retrieve data for. If
                :code:`since` is not None, this is ignored. This
                accounts for delayed revenue analytics, but does mean
                that an extra day of data may sometimes be included in
                the report. Defaults to 28.
            metrics (iterable[str] | str): A list of metrics to use.
                Defaults to "all".

        Returns:
            YouTubeAnalyticsReport: The retrieved report.

        Raises:
            InvalidRequest: Something is wrong with the request.
            HTTPError: The API returned an error.
        """
        return self.retrieve(
            since or dt.date.today() - dt.timedelta(days=last + 2),
            dimensions=("country",),
            metrics=metrics,
            sort_by=("-views",),
        )

    def top_videos(self, by="views", since=None, last=28, metrics="all"):
        """A factory method that retrieves information on your channel's
        top videos over time.

        .. versionadded:: 2.1

        Keyword Args:
            by (str): The metric to sort by. Note that not all metrics
                are supported. Reports retrieved using this method will
                be sorted in descending order regardless of whether you
                prefix the metric with a hyphen (-). Defaults to
                "views".
            since (datetime.date | None): The date to start collecting
                data from. If this is None, analytix will fall back to
                the :code:`last` kwarg. Defaults to None.
            last (int): The number of days to retrieve data for. If
                :code:`since` is not None, this is ignored. This
                accounts for delayed revenue analytics, but does mean
                that an extra day of data may sometimes be included in
                the report. Defaults to 28.
            metrics (iterable[str] | str): A list of metrics to use.
                Defaults to "all".

        Returns:
            YouTubeAnalyticsReport: The retrieved report.

        Raises:
            InvalidRequest: Something is wrong with the request.
            HTTPError: The API returned an error.
        """
        return self.retrieve(
            since or dt.date.today() - dt.timedelta(days=last + 2),
            dimensions=("video",),
            metrics=metrics,
            sort_by=(f"-{by.strip('-')}",),
            max_results=200,
        )


class YouTubeAnalyticsReport:
    """A class created when a report is retrieved. You should not
    attempt to construct this class manually.

    Args:
        type (str): The report type.
        data (dict[str, Any]): The raw data from the YouTube Analytics
            API.

    Attributes:
        type (str): The report type.
        data (dict[str, Any]): The raw data from the YouTube Analytics
            API.
        columns (list[str]): A list of all column names.
    """

    __slots__ = ("type", "data", "columns", "_ncolumns", "_nrows")

    def __init__(self, type, data):
        self.type = type
        self.data = data
        self.columns = [c["name"] for c in data["columnHeaders"]]
        self._ncolumns = len(self.columns)
        self._nrows = len(data["rows"])

    def __repr__(self):
        return f"<YouTubeAnalyticsReport shape={self.shape!r}>"

    @property
    def shape(self):
        """The shape of the report.

        Returns:
            tuple[int, int]: Number of rows, columns.
        """
        return (self._nrows, self._ncolumns)

    def to_dataframe(self):
        """Returns the data in a pandas DataFrame. If "day" or "month"
        are columns, these are converted to the datetime64[ns] dtype
        automatically.

        Returns:
            DataFrame: A pandas DataFrame
        """
        if not PANDAS_AVAILABLE:
            raise MissingOptionalComponents("pandas is not installed")

        df = pd.DataFrame(self.data["rows"])
        df.columns = self.columns
        if "day" in df.columns:
            df["day"] = pd.to_datetime(df["day"], format="%Y-%m-%d")
        if "month" in df.columns:
            df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
        return df

    def to_json(self, path, *, indent=4):
        """Writes the raw report data to a JSON file.

        Args:
            path (str): The path to save the file to.

        Keyword Args:
            indent (int): The amount of spaces to use as an indent.
                Defaults to 4.
        """
        if not path.endswith(".json"):
            path += ".json"

        with open(path, mode="w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=indent, ensure_ascii=False)

    def to_csv(self, path, *, delimiter=","):
        """Writes the report data to a CSV file.

        Args:
            path (str): The path to save the file to.

        Keyword Args:
            delimiter (int): The delimiter to use to separate columns.
                Defaults to a comma (,).
        """
        if not path.endswith(".csv"):
            path += ".csv"

        with open(path, mode="w", encoding="utf-8") as f:
            f.write(f"{delimiter.join(self.columns)}\n")
            for row in self.data["rows"]:
                f.write(f"{delimiter.join(f'{i}' for i in row)}\n")
