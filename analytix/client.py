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

"""A module containing the client interface.

The client authenticates using OAuth 2. This means you will need to
have a Google Developers project with the YouTube Analytics API enabled.
You can find out how to do that in the API setup guide.
"""

from __future__ import annotations

__all__ = ("Client",)

import datetime
import logging
import pathlib
import typing as t

import requests as rq

import analytix
from analytix import errors, oauth
from analytix.groups import GroupItemList, GroupList
from analytix.oauth import Secrets, Tokens
from analytix.queries import GroupItemQuery, GroupQuery, ReportQuery
from analytix.reports import AnalyticsReport
from analytix.webserver import Server

if t.TYPE_CHECKING:
    from analytix.types import PathLikeT

_log = logging.getLogger(__name__)


class Client:
    """A class representing a client for the YouTube Analytics API.

    Parameters
    ----------
    secrets_file : Path object or str
        The path to your secrets file. This is relative from your
        current working directory.
    tokens_file : Path object or str
        The path to your token file. This is relative from your current
        working directory.
    ws_port : int
        The port to use for webserver authorisation.

    Attributes
    ----------
    secrets : Secrets
        A `Secrets` object represting your client secrets.

    Examples
    --------
    ```py
    >>> client = Client("secrets.json")

    # If you wanted to specify a custom token dir and webserver port:
    >>> client = Client(
    ...     "secrets/secrets.json",
    ...     tokens_file="secrets/tokens.json",
    ...     ws_port=9999,
    ... )
    ```
    """

    __slots__ = ("secrets", "_token_path", "_tokens", "_ws_port", "_update_checked")

    def __init__(
        self,
        secrets_file: PathLikeT,
        *,
        tokens_file: PathLikeT = "tokens.json",
        ws_port: int = 8080,
    ) -> None:
        self.secrets = Secrets.from_file(secrets_file)

        if not isinstance(tokens_file, pathlib.Path):
            tokens_file = pathlib.Path(tokens_file)

        if tokens_file.is_dir():
            tokens_file = tokens_file / "tokens.json"

        self._token_path = tokens_file
        self._tokens: Tokens | None = None
        self._ws_port = ws_port
        self._update_checked = False

    def __str__(self) -> str:
        return self.secrets.project_id

    def __repr__(self) -> str:
        return f"Client(project_id={self.secrets.project_id})"

    @property
    def is_authorised(self) -> bool:
        """Whether this client is authorised.

        This property is read-only.

        Returns
        -------
        bool
            Whether this client is authorised.
        """

        return self._tokens is not None

    def _request(self, url: str) -> t.Any:
        assert self._tokens is not None

        headers = {"Authorization": f"Bearer {self._tokens.access_token}"}
        resp = rq.get(url, headers=headers)

        if not resp.ok:
            raise errors.APIError(str(resp.status_code), resp.reason)

        data = resp.json()
        _log.debug(f"Data retrieved: {data}")

        if next(iter(data)) == "error":
            error = data["error"]
            raise errors.APIError(error["code"], error["message"])

        return data

    def can_update(self) -> bool:
        """Determine if analytix can be updated.

        Returns
        -------
        bool
            Whether analytix can be updated.
        """

        _log.debug("Checking for updates...")

        resp = rq.get(analytix.UPDATE_CHECK_URL)
        if not resp.ok:
            # If we can't get the info, just ignore it.
            _log.debug("Failed to get version information")
            return False

        self._update_checked = True
        latest: str = resp.json()["info"]["version"]
        return analytix.__version__ != latest

    def _try_load_tokens(self) -> Tokens | None:
        if not self._token_path.is_file():
            return None

        return Tokens.from_file(self._token_path)

    def _retrieve_tokens(self) -> Tokens:
        rd_url = self.secrets.redirect_uris[-1]
        rd_addr = f"{rd_url}:{self._ws_port}"

        url, _ = oauth.auth_url_and_state(self.secrets, rd_addr)
        print(
            "\33[38;5;45mYou need to authorise analytix. "
            f"To do so, visit this URL:\33[0m \33[4m{url}\33[0m"
        )

        ws = Server(rd_url[7:], self._ws_port)
        try:
            ws.handle_request()
        except KeyboardInterrupt as exc:
            raise exc
        finally:
            ws.server_close()

        data, headers = oauth.access_data_and_headers(ws.code, self.secrets, rd_addr)
        resp = rq.post(self.secrets.token_uri, data=data, headers=headers)
        if not resp.ok:
            raise errors.AuthenticationError(**resp.json())

        return Tokens.from_json(resp.json())

    def authorise(self, *, force: bool = False) -> Tokens:
        """Authorise this client.

        While this can be called manually, the client will automatically
        authorise itself when necessary. Once the tokens have been
        retrieved, they will be written to the filepath you passed when
        instantiating the instance.

        Parameters
        ----------
        force : bool
            Whether to force authorisation, even if this client is
            already authorised.

        Returns
        -------
        Tokens
            An object representing your API tokens.
        """

        if not force:
            _log.info("Attempting to load tokens from disk...")
            self._tokens = self._try_load_tokens()

        if not self._tokens:
            _log.info("Unable to load tokens — you will need to authorise")
            self._tokens = self._retrieve_tokens()
            self._tokens.write(self._token_path)

        _log.info("Authorisation complete!")
        return self._tokens

    def needs_token_refresh(self) -> bool:
        """Determine if this client's refresh tokens need to be
        refreshed.

        Much like `authorise()` this is called automatically when
        needed, but can be called manually if you so wish.

        Returns
        -------
        bool
            Whether the refresh tokens need to be refreshed.

        !!! note
            If the client is authorised, this will always return
            `False`.
        """

        if not self._tokens:
            # Can't refresh if they're non-existent.
            return False

        _log.debug("Checking if access token needs to be refreshed...")
        resp = rq.get(analytix.OAUTH_CHECK_URL + self._tokens.access_token)
        return not resp.ok

    def refresh_access_token(self) -> None:
        """Refreshes this client's access tokens.

        Much like `authorise()` this is called automatically when
        needed, but can be called manually if you so wish. It should
        normally be called in tandum with `needs_token_refresh()` unless
        you want to forcibly refresh the token for whatever reason.
        """

        if not self._tokens:
            _log.warning(
                "There are no tokens to refresh — this may have been called in error"
            )
            return

        _log.info("Refreshing access token...")
        data, headers = oauth.refresh_data_and_headers(
            self._tokens.refresh_token, self.secrets
        )

        resp = rq.post(self.secrets.token_uri, data=data, headers=headers)
        if resp.ok:
            self._tokens.update(resp.json())
        else:
            _log.info("Your refresh token has expired — you will need to reauthorise")
            self._tokens = self._retrieve_tokens()

        self._tokens.write(self._token_path)

    def retrieve_report(
        self,
        *,
        dimensions: t.Collection[str] | None = None,
        filters: dict[str, str] | None = None,
        metrics: t.Collection[str] | None = None,
        sort_options: t.Collection[str] | None = None,
        max_results: int = 0,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        currency: str = "USD",
        start_index: int = 1,
        include_historical_data: bool = False,
        force_authorisation: bool = False,
        skip_update_check: bool = False,
    ) -> AnalyticsReport:
        """Retrieve a report from the YouTube Analytics API.

        If the client is not already authorised, it will do so
        automatically after verification.

        Parameters
        ----------
        dimensions : collection of str
            The dimensions to use in the report. More information on
            dimensions can be found in
            [the dimensions guide](../../guides/dimensions). If this is
            not provided, no dimensions will be used.
        filters : dict of str-str
            The filters to use in the report. More information on
            filters can be found in
            [the filters guide](../../guides/filters). If this is not
            provided, no filters will be used.
        metrics : collection of str
            The metrics to use in the report. More information on
            metrics can be found in
            [the metrics guide](../../guides/metrics). If this is not
            provided, all valid metrics will be used (the list of valid
            metrics will be determined automatically).
        sort_options : collection of str
            The sort options to use in the report. More information on
            sort options can be found in
            [the sort options guide](../../guides/sort_options). If this
            is not provided, no sort options will be used.
        max_results : int
            The maximum number of results to use in the report. If this
            is `0`, all results are included.
        start_date : date object
            The date to start pulling data from. If this is not
            provided, this is set to 28 days before the end date.
        end_date : date object
            The date to pull data to. If this is not provided, this is
            set to the current date.
        currency : str
            The currency to use for revenue data as an ISO 4217 currency
            code.
        start_index : int
            The first result to include in the report. This value is
            one-indexed, meaning result `1` is the first result. If this
            is `1`, all results are included.
        include_historical_data : bool
            Whether to include data from before the current channel
            owner became the owner. For example, if this is `False`, and
            the current channel owner assumed ownership on 1 Jan 2022,
            no data before that point would be retrieved, even if
            `start_date` was set before that point. If you are the
            original owner of your channel, you don't need to worry
            about this.

        Returns
        -------
        AnalyticsReport
            An object representing an analytics report.

        Other Parameters
        ----------------
        force_authorisation : bool
            Whether to force client authorisation, even if the client
            is already authorised.
        skip_update_check : bool
            Whether to skip checking whether you have the latest version
            of analytix.

        Raises
        ------
        APIError
            An error occurred when retrieving the report.

        !!! warning
            If `end_date` is set to (or near to) the current date, some
            report results may be missing due to delays with YouTube's
            processing of revenue data.

        !!! important
            To get information on playlists, include "isCurated" in your
            filters, and set the value to "1" (example below).

        !!! note
            Some report types require a maximum number of results to be
            provided.

        Examples
        --------
        ```py
        >>> client.retrieve_report()

        # Retrieve day-to-day views, likes, and comments in 2021.
        >>> client.retrieve_report(
        ...     dimensions=("day",),
        ...     metrics=("views", "likes", "comments"),
        ...     start_date=datetime.date(2021, 1, 1),
        ...     end_date=datetime.date(2021, 12, 31),
        ... )

        # Retrieve US analytics on playlists.
        >>> client.retrieve_report(
        ...     filters={"isCurated": "1", "country": "US"}
        ... )
        ```
        """

        if not skip_update_check and not self._update_checked:
            if self.can_update():
                _log.warning("You do not have the latest stable version of analytix")

        query = ReportQuery(
            dimensions,
            filters,
            metrics,
            sort_options,
            max_results,
            start_date,
            end_date,
            currency,
            start_index,
            include_historical_data,
        )
        query.validate()

        if not self.is_authorised or force_authorisation:
            self.authorise(force=force_authorisation)

        if self.needs_token_refresh():
            self.refresh_access_token()

        data = self._request(query.url)

        if not query.rtype:
            query.set_report_type()

        assert query.rtype is not None
        report = AnalyticsReport(data, query.rtype)
        _log.info(f"Created report of shape {report.shape}!")
        return report

    def fetch_groups(
        self,
        *,
        ids: t.Collection[str] | None = None,
        next_page_token: str | None = None,
        force_authorisation: bool = False,
        skip_update_check: bool = False,
    ) -> GroupList:
        """Fetch groups from the YouTube Analytics API.

        If the client is not already authorised, it will do so
        automatically.

        Parameters
        ----------
        ids : collection of str
            The IDs of the groups you want to fetch. If this is not
            provided, all groups will be fetched.
        next_page_token : str
            Retrieve the next page of results. You probably don't need
            to worry about this unless you have a very large number of
            groups. If this is not provided, the first page of results
            will be fetched.
        force_authorisation : bool
            Whether to force client authorisation, even if the client
            is already authorised.
        skip_update_check : bool
            Whether to skip checking whether you have the latest version
            of analytix.

        Returns
        -------
        GroupList
            An object representing a groupListResponse.

        Raises
        ------
        APIError
            An error occurred when retrieving the report.

        !!! note
            A next page token is always included irrespective of how
            many pages there are in the results. The only way to tell
            if you've exhausted the search is to make a request with
            that token and compare that request's token to that of the
            first request you made.

        Examples
        --------
        ```py
        >>> client.fetch_groups()

        # Fetch specific groups.
        >>> client.fetch_groups(ids=("38fh93bgm", "fj983gn89b"))
        ```
        """

        if not skip_update_check and not self._update_checked:
            if self.can_update():
                _log.warning("You do not have the latest stable version of analytix")

        if not self.is_authorised or force_authorisation:
            self.authorise()

        if self.needs_token_refresh():
            self.refresh_access_token()

        query = GroupQuery(ids, next_page_token)
        return GroupList.from_json(self._request(query.url))

    def fetch_group_items(
        self,
        group_id: str,
        *,
        force_authorisation: bool = False,
        skip_update_check: bool = False,
    ) -> GroupItemList:
        """Fetch items for a group from the YouTube Analytics API.

        If the client is not already authorised, it will do so
        automatically.

        Parameters
        ----------
        group_id : str
            The ID of the group whose items you want to fetch.
        force_authorisation : bool
            Whether to force client authorisation, even if the client
            is already authorised.
        skip_update_check : bool
            Whether to skip checking whether you have the latest version
            of analytix.

        Returns
        -------
        GroupItemList
            An object representing a groupItemListResponse.

        Raises
        ------
        APIError
            An error occurred when retrieving the report.

        Examples
        --------
        >>> client.fetch_group_items("38fh93bgm")
        """

        if not skip_update_check and not self._update_checked:
            if self.can_update():
                _log.warning("You do not have the latest stable version of analytix")

        if not self.is_authorised or force_authorisation:
            self.authorise()

        if self.needs_token_refresh():
            self.refresh_access_token()

        query = GroupItemQuery(group_id)
        return GroupItemList.from_json(self._request(query.url))
