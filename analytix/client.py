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

"""Client interfaces for analytix."""

__all__ = ("Client",)

import datetime as dt
import json
import logging
from collections.abc import Collection
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import cast

from analytix.auth.scopes import Scopes
from analytix.auth.secrets import Secrets
from analytix.auth.tokens import Tokens
from analytix.groups import GroupItemList
from analytix.groups import GroupList
from analytix.mixins import RequestMixin
from analytix.queries import GroupItemQuery
from analytix.queries import GroupQuery
from analytix.queries import ReportQuery
from analytix.reports import Report

if TYPE_CHECKING:
    from analytix.abc import ReportType
    from analytix.types import PathLike


UPDATE_CHECK_URL = "https://pypi.org/pypi/analytix/json"

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class SessionContext:
    access_token: str
    scopes: Scopes


class Client(RequestMixin):
    """A client for the YouTube Analytics API.

    ??? note "Changed in version 6.0"
        * Removed `ws_port` and `auto_open_browser` parameters
        * This is now the only client class

    Parameters
    ----------
    secrets_file
        The path to your secrets file.
    tokens_file
        The path to save your tokens to. This must be a JSON file, but
        does not need to exist. Passing `None` will disable token
        saving. If this is not provided, your tokens will be saved to a
        file called "tokens.json" in your current working directory.
    scopes
        The scopes to allow in requests. The default scopes do not allow
        the fetching of monetary data.
    """

    __slots__ = ("_secrets", "_session_ctx", "_tokens_file")

    def __init__(
        self,
        secrets_file: "PathLike",
        *,
        tokens_file: str | Path | None = "tokens.json",
        scopes: Scopes = Scopes.READONLY,
    ):
        scopes.validate()
        self._secrets = Secrets.load_from(secrets_file, scopes)
        self._session_ctx: SessionContext | None = None
        self._tokens_file: Path | None

        if tokens_file:
            self._tokens_file = Path(tokens_file)
            if self._tokens_file.suffix != ".json":
                raise ValueError("tokens file must be a JSON file")
        else:
            self._tokens_file = None

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *_: object) -> None:
        pass

    @property
    def secrets(self) -> Secrets:
        """Your secrets.

        Returns
        -------
        Secrets
            Your secrets.
        """
        return self._secrets

    def authorise(
        self,
        *,
        force: bool = False,
        ws_port: int | None = None,
        console: bool = False,
    ) -> Tokens:
        """Authorise the client.

        You only need to call this manually if you want to customise
        the authorisation flow. The client will authorise itself
        automatically when needed otherwise.

        ??? note "Changed in version 6.0"
            * Added `ws_port` and `console` parameters.
            * Removed `force_refresh` parameter.

        Parameters
        ----------
        force
            Whether to forcibly authorise the client. If this is not
            provided, the client will only authorise if needed.
        ws_port : int, optional
            The port the client's webserver will use during
            authorisation. If this is not provided, a sensible default
            will be used (normally `80` or `8080`).
        console
            Whether to bypass the browser and authorise in the console.
            If this is not provided, the client will try to open the
            browser first.

        Returns
        -------
        Tokens
            Your tokens.
        """
        if not force and self._tokens_file and self._tokens_file.is_file():
            tokens = Tokens.load_from(self._tokens_file)
            if tokens.are_scoped_for(self._secrets.scopes) and (
                not tokens.expired or self.refresh_tokens(tokens)
            ):
                _log.info("Authorisation complete!")
                return tokens

        _log.info("The client needs to be authorised, starting flow...")

        with self._secrets.auth_context(ws_port=ws_port) as ctx:
            if console or not ctx.open_browser():
                print(  # noqa: T201
                    f"Follow this link to authorise the client: {ctx.auth_uri}",
                )

            tokens = ctx.fetch_tokens()
            if self._tokens_file:
                tokens.save_to(self._tokens_file)

            _log.info("Authorisation complete!")
            return tokens

    def refresh_tokens(self, tokens: Tokens) -> Tokens | None:
        """Refresh and save your tokens.

        This is a convenience method to refresh your tokens and save
        them to disk at the same time. If you want more control over
        this behaviour, use the methods in the See Also section instead.

        !!! note "New in version 6.0"

        Parameters
        ----------
        tokens
            Your tokens.

        Returns
        -------
        Optional[Tokens]
            Your refreshed tokens, or `None` if they could not be
            refreshed. In the latter instance, your client will need to
            be reauthorised from scratch.

        See Also
        --------
        * `Tokens.refresh`
        * `Tokens.save_to`
        """
        refreshed = tokens.refresh(self._secrets)

        if not refreshed:
            return None

        if self._tokens_file:
            tokens.save_to(self._tokens_file)

        return tokens

    @contextmanager
    def session(
        self,
        tokens: Tokens | None = None,
        scopes: Scopes | None = None,
    ) -> Iterator[None]:
        """Create a session.

        When you create a session, the client will authorise the session
        and reuse the credentials across all requests within it. This
        helps reduce the amount of times the client needs to authorise
        itself.

        This method is a context manager.

        !!! note "New in version 6.0"

        Parameters
        ----------
        tokens
            Your tokens. If this is not provided, the client will
            authorise itself.
        scopes
            The scopes to use for this session. If this is not provided,
            the scopes given to the client will be used.

        Yields
        ------
        None
            This method doesn't yield anything.

        Examples
        --------
        >>> with client.session():
        ...     for year in range(2019, 2024):
        ...         client.fetch_report(
        ...             start_date=dt.date(year, 1, 1),
        ...             end_date=dt.date(year, 12, 31),
        ...         )
        """
        if not tokens:
            tokens = self.authorise()

        self._session_ctx = SessionContext(
            access_token=tokens.access_token,
            scopes=scopes or self._secrets.scopes,
        )
        _log.debug("New client session created")
        yield
        self._session_ctx = None

    def fetch_report(
        self,
        *,
        dimensions: Collection[str] | None = None,
        filters: dict[str, str] | None = None,
        metrics: Collection[str] | None = None,
        start_date: dt.date | None = None,
        end_date: dt.date | None = None,
        sort_options: Collection[str] | None = None,
        max_results: int = 0,
        currency: str = "USD",
        start_index: int = 1,
        include_historical_data: bool = False,
        tokens: Tokens | None = None,
        scopes: Scopes | None = None,
    ) -> "Report":
        """Fetch an analytics report.

        ??? note "Changed in version 6.0"
            You can now pass tokens and scopes directly to this method.
            To customise the authorisation flow, you should pass tokens
            directly instead of kwargs for the `authorise` method.

        Parameters
        ----------
        dimensions
            The dimensions to use within the request.
        filters
            The filters to use within the request.
        metrics
            The metrics to use within the request. If none are provided,
            all supported metrics are used.
        sort_options
            The sort options to use within the request.
        start_date
            The date in which data should be pulled from. If this is
            not provided, this is set to 28 days before `end_date`.
        end_date
            The date in which data should be pulled to. If this is not
            provided, this is set to the current date.
        max_results
            The maximum number of results the report should include. If
            this is `0`, no upper limit is applied.
        currency
            The currency revenue data should be represented using. This
            should be an ISO 4217 currency code.
        start_index
            The first row in the report to include. This is one-indexed.
            If this is `1`, all rows are included.
        include_historical_data
            Whether to include data from before the current channel
            owner assumed control of the channel. You only need to worry
            about this is the current channel owner did not create the
            channel.

        Returns
        -------
        Report
            The generated report.

        Other Parameters
        ----------------
        tokens
            Your tokens. If this is not provided, session tokens will be
            used if present, otherwise the client will authorise itself.
        scopes
            The scopes to use for this request. If this is not provided,
            the scopes given to the client will be used.

        Raises
        ------
        InvalidRequest
            Your request was invalid.
        BadRequest
            Your request was invalid, but it was not caught by
            analytix's verification systems.
        Unauthorised
            Your access token is invalid.
        Forbidden
            You tried to access data you're not allowed to access. If
            your channel is not partnered, this is raised when you try
            to access monetary data.
        AuthorisationError
            Something went wrong during authorisation.

        Warnings
        --------
        * If your channel is not partnered, attempting to access
          monetary data will result in a `Forbidden` error. Ensure your
          scopes are set up correctly before calling this method.
        * The "isCurated" filter stopped working on 30 Jun 2024. See the
          [guide on new playlist reports](../guides/new-playlist-reports.md)
          for information on how to migrate.

        See Also
        --------
        You can learn more about dimensions, filters, metrics, and sort
        options by reading the [detailed guides](../guides/
        dimensions.md).

        Examples
        --------
        Fetching daily analytics data for 2022.

        >>> import datetime
        >>> client.fetch_report(
        ...     dimensions=("day",),
        ...     start_date=datetime.date(2022, 1, 1),
        ...     end_date=datetime.date(2022, 12, 31),
        ... )

        Fetching 10 most watched videos over last 28 days.

        >>> client.fetch_report(
        ...     dimensions=("video",),
        ...     metrics=("estimatedMinutesWatched", "views"),
        ...     sort_options=("-estimatedMinutesWatched",),
        ...     max_results=10,
        ... )
        """
        access_token = (tokens or self._session_ctx or self.authorise()).access_token
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
        query.validate(scopes or self._secrets.scopes)

        with self._request(query.url, token=access_token) as resp:
            data = json.loads(resp.data)

        report = Report(data, cast("ReportType", query.rtype))
        _log.info("Created '%s' report of shape %s", query.rtype, report.shape)
        return report

    def fetch_groups(
        self,
        *,
        ids: Collection[str] | None = None,
        next_page_token: str | None = None,
        tokens: Tokens | None = None,
    ) -> "GroupList":
        """Fetch a list of analytics groups.

        ??? note "Changed in version 6.0"
            You can now pass tokens directly to this method. To
            customise the authorisation flow, you should pass tokens
            directly instead of kwargs for the `authorise` method.

        Parameters
        ----------
        ids
            The IDs of groups you want to fetch. If none are provided,
            all your groups will be fetched.
        next_page_token
            If you need to make multiple requests, you can pass this to
            load a specific page. To check if you've arrived back at the
            first page, check the next page token from the request and
            compare it to the next page token from the first page.

        Other Parameters
        ----------------
        tokens
            Your tokens. If this is not provided, session tokens will be
            used if present, otherwise the client will authorise itself.

        Returns
        -------
        GroupList
            An object containing the list of your groups and the next
            page token.

        Raises
        ------
        BadRequest
            Your request was invalid.
        Unauthorised
            Your access token is invalid.
        Forbidden
            You tried to access data you're not allowed to access. If
            your channel is not partnered, this is raised when you try
            to access monetary data.
        RuntimeError
            The client attempted to open a new browser tab, but failed.
        AuthorisationError
            Something went wrong during authorisation.
        """
        access_token = (tokens or self._session_ctx or self.authorise()).access_token
        query = GroupQuery(ids, next_page_token)
        with self._request(query.url, token=access_token) as resp:
            return GroupList.from_json(self, json.loads(resp.data))

    def fetch_group_items(
        self,
        group_id: str,
        tokens: Tokens | None = None,
    ) -> "GroupItemList":
        """Fetch a list of all items within a group.

        ??? note "Changed in version 6.0"
            You can now pass tokens directly to this method. To
            customise the authorisation flow, you should pass tokens
            directly instead of kwargs for the `authorise` method.

        Parameters
        ----------
        group_id
            The ID of the group to fetch items for.

        Other Parameters
        ----------------
        tokens
            Your tokens. If this is not provided, session tokens will be
            used if present, otherwise the client will authorise itself.

        Returns
        -------
        GroupItemList
            An object containing the list of group items and the next
            page token.

        Raises
        ------
        BadRequest
            Your request was invalid.
        Unauthorised
            Your access token is invalid.
        Forbidden
            You tried to access data you're not allowed to access. If
            your channel is not partnered, this is raised when you try
            to access monetary data.
        RuntimeError
            The client attempted to open a new browser tab, but failed.
        AuthorisationError
            Something went wrong during authorisation.
        """
        access_token = (tokens or self._session_ctx or self.authorise()).access_token
        query = GroupItemQuery(group_id)
        with self._request(query.url, token=access_token) as resp:
            return GroupItemList.from_json(json.loads(resp.data))
