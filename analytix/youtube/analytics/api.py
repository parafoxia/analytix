import csv
import datetime as dt
import json
import logging
import os
import time
import typing as t

import requests
from requests_oauthlib import OAuth2Session

from analytix.errors import *
from analytix.iso import CURRENCIES
from analytix.packages import *
from analytix.secrets import TOKEN_STORE, YT_ANALYTICS_TOKEN
from analytix.youtube.analytics import *
from analytix.youtube.analytics import verify

if PANDAS_AVAILABLE:
    import pandas as pd
if NUMPY_AVAILABLE:
    import numpy as np


class YouTubeAnalytics:
    __slots__ = ("_session", "secrets", "project_id", "_token")

    def __init__(self, session, secrets, **kwargs):
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
        return bool(self._token)

    authorized = authorised

    @classmethod
    def from_file(cls, path, *, scopes="all", **kwargs):
        if not os.path.isfile(path):
            raise FileNotFoundError(
                "you must provide a valid path to a secrets file"
            )

        with open(path, mode="r", encoding="utf-8") as f:
            logging.debug("Secrets file loaded")
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
            logging.debug(f"Scopes set to {YOUTUBE_ANALYTICS_SCOPES}")
            return YOUTUBE_ANALYTICS_SCOPES

        if not isinstance(scopes, (tuple, list, set)):
            raise InvalidScopes(
                f"expected tuple, list, or set of scopes, got {type(scopes).__name__}"
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

        logging.debug(f"Scopes set to {scopes}")
        return scopes

    @staticmethod
    def _get_token():
        if not os.path.isfile(TOKEN_STORE / YT_ANALYTICS_TOKEN):
            logging.info("No token found. You will need to authorise")
            return ""

        with open(
            TOKEN_STORE / YT_ANALYTICS_TOKEN, mode="r", encoding="utf-8"
        ) as f:
            data = json.load(f)
        if time.time() > data["expires"]:
            logging.info(
                "Token found, but it has expired. You will need to authorise"
            )
            return ""

        logging.info(
            "Valid token found! analytix will use this, so you don't need to authorise"
        )
        return data["token"]

    def authorise(self, store_token=True, force=False, **kwargs):
        if self._token and not force:
            logging.warning("Client is already authorised! Skipping...")
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
        logging.info("Token retrieved")

        if not store_token:
            logging.info("Not storing token, as instructed")
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
            logging.info(f"Key stored in {TOKEN_STORE / YT_ANALYTICS_TOKEN}")

    authorize = authorise

    def retrieve(
        self, start_date, end_date=dt.date.today(), metrics="all", **kwargs
    ):
        currency = kwargs.pop("currency", "USD")
        dimensions = kwargs.pop("dimensions", ())
        filters = kwargs.pop("filters", {})
        include_historical_data = kwargs.pop("include_historical_data", False)
        max_results = kwargs.pop("max_results", 0)
        sort_by = kwargs.pop("sort_by", ())
        start_index = kwargs.pop("start_index", 1)

        logging.debug("Verifying options...")
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
                f"expected existing currency as ISO 4217 alpha-3 code, got {currency}"
            )
        if not isinstance(dimensions, (tuple, list, set)):
            raise InvalidRequest(
                f"expected tuple, list, or set of dimensions, got {type(dimensions).__name__}"
            )
        if not isinstance(filters, dict):
            raise InvalidRequest(
                f"expected dict of filters, got {type(filters).__name__}"
            )
        if not isinstance(include_historical_data, bool):
            raise InvalidRequest(
                f"expected bool for 'include_historical_data', got {type(include_historical_data).__name__}"
            )
        if not isinstance(max_results, int):
            raise InvalidRequest(
                f"expected int for 'max_results', got {type(max_results).__name__}"
            )
        if max_results < 0:
            raise InvalidRequest(
                f"the maximum number of results should be no less than 0 (0 for unlimited results)"
            )
        if not isinstance(sort_by, (tuple, list, set)):
            raise InvalidRequest(
                f"expected tuple, list, or set of sorting columns, got {type(sort_by).__name__}"
            )
        if not isinstance(start_index, int):
            raise InvalidRequest(
                f"expected int for 'start_index', got {type(start_index).__name__}"
            )
        if start_index < 1:
            raise InvalidRequest(f"the start index should be no less than 1")

        logging.debug("Determining report type...")
        rtype = verify.rtypes.determine(dimensions, metrics, filters)()
        logging.info(f"Report type determined as: {rtype}")

        if metrics == "all":
            metrics = tuple(rtype.metrics)
        elif not isinstance(metrics, (tuple, list, set)):
            raise InvalidRequest(
                f"expected tuple, list, or set of metrics, got {type(metrics).__name__}"
            )
        logging.debug("Using these metrics: " + ", ".join(metrics))

        logging.debug("Verifying report...")
        rtype.verify(dimensions, metrics, filters, max_results, sort_by)
        logging.debug("Verification complete")

        url = (
            f"https://youtubeanalytics.googleapis.com/{YOUTUBE_ANALYTICS_API_VERSION}/reports"
            "?ids=channel==MINE"
            f"&metrics={','.join(metrics)}"
            f"&startDate={start_date.strftime('%Y-%m-%d')}"
            f"&endDate={end_date.strftime('%Y-%m-%d')}"
            f"&currency={currency}"
            f"&dimensions={','.join(dimensions)}"
            f"&filters={';'.join(f'{k}=={v}' for k, v in filters.items())}"
            f"&includeHistorialChannelData={f'{include_historical_data}'.lower()}"
            f"&maxResults={max_results}"
            f"&sort={','.join(sort_by)}"
            f"&startIndex={start_index}"
        )
        logging.debug(f"URL: {url}")

        if not self._token:
            self.authorise()

        with requests.get(
            url, headers={"Authorization": f"Bearer {self._token}"}
        ) as r:
            data = r.json()

        if next(iter(data)) == "error":
            error = data["error"]
            raise HTTPError(f"{error['code']}: {error['message']}")

        logging.info("Creating report...")
        return YouTubeAnalyticsReport(
            f"{rtype}", [c["name"] for c in data["columnHeaders"]], data["rows"]
        )


class YouTubeAnalyticsReport:
    __slots__ = ("type", "columns", "rows", "_ncolumns", "_nrows")

    def __init__(self, type, columns, rows):
        self.type = type
        self.columns = columns
        if NUMPY_AVAILABLE:
            self.rows = np.array(rows)
        else:
            self.rows = rows
        self._ncolumns = len(self.columns)
        self._nrows = len(self.rows)

    def __repr__(self):
        return f"<YouTubeAnalyticsReport shape={self.shape!r}>"

    @property
    def shape(self):
        return (self._nrows, self._ncolumns)

    @requires_pandas
    def to_dataframe(self):
        df = pd.DataFrame(self.rows)
        df.columns = self.columns
        if "day" in df.columns:
            df["day"] = pd.to_datetime(df["day"], format="%Y-%m-%d")
        if "month" in df.columns:
            df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
        return df

    def to_csv(self, path, *, delimiter=","):
        if not path.endswith(".csv"):
            path += ".csv"

        with open(path, mode="w", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(self.columns)
            for r in self.rows:
                writer.writerow(r)
