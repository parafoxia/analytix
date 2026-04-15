# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

"""Client interfaces for analytix."""

__all__ = ("Client",)

import datetime as dt
import json
import logging
from collections.abc import Collection
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Self

from .auth.scopes import Scopes
from .auth.secrets import Secrets
from .auth.tokens import Tokens
from .groups import GroupItemList
from .groups import GroupList
from .mixins import RequestMixin
from .queries import GroupItemQuery
from .queries import GroupQuery
from .reports.builder import ReportBuilder
from .reports.interfaces import Report
from .reports.types import ReportType
from .session import Session

if TYPE_CHECKING:
    from analytix.types import PathLike


UPDATE_CHECK_URL = "https://pypi.org/pypi/analytix/json"

_log = logging.getLogger(__name__)


class Client(RequestMixin):
    """A client for the YouTube Analytics API.

    ??? note "Changed in version 6.0"
        * Removed `ws_port` and `auto_open_browser` parameters

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

    __slots__ = ("_secrets", "_session", "_tokens_file")

    def __init__(
        self,
        secrets_file: "PathLike",
        *,
        tokens_file: str | Path | None = "tokens.json",
        scopes: Scopes = Scopes.READONLY,
    ):
        scopes.validate()
        self._secrets = Secrets.read_json(secrets_file, scopes)
        self._session: Session | None = None
        self._tokens_file: Path | None

        if tokens_file:
            self._tokens_file = Path(tokens_file)
            if self._tokens_file.suffix != ".json":
                raise ValueError("tokens file must be a JSON file")
        else:
            self._tokens_file = None

    def __enter__(self) -> Self:
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
            * Added `ws_port` and `console` parameters
            * Removed `force_refresh` parameter

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
            tokens = Tokens.read_json(self._tokens_file)
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
                tokens.to_json(self._tokens_file)

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
        * `Tokens.to_json`
        """
        refreshed = tokens.refresh(self._secrets)

        if not refreshed:
            return None

        if self._tokens_file:
            tokens.to_json(self._tokens_file)

        return tokens

    def _create_session(
        self,
        key: str = "default",
        tokens: Tokens | None = None,
        scopes: Scopes | None = None,
    ) -> Session:
        if not tokens:
            tokens = self.authorise()

        return Session(
            key=key,
            access_token=tokens.access_token,
            scopes=scopes or self._secrets.scopes,
        )

    @contextmanager
    def session(
        self,
        key: str = "default",
        tokens: Tokens | None = None,
        scopes: Scopes | None = None,
    ) -> Iterator[Session]:
        """Create a session.

        When you create a session, the client will authorise the session
        and reuse the credentials across all requests within it. This
        helps reduce the amount of times the client needs to authorise
        itself.

        The default behaviour is to create a session which is then
        destroyed when the context manager exits. If you wish to create
        and manage multiple persistent sessions, you can override this
        method to provide that functionality.

        Generally speaking, sessions should not live for too long as
        they are not able to refresh their own tokens.

        This method is a context manager.

        !!! note "New in version 6.0"

        Parameters
        ----------
        key
            The key to use for this session. This is useful when
            managing multiple sessions.
        tokens
            Your tokens. If this is not provided, the client will
            authorise itself.
        scopes
            The scopes to use for this session. If this is not provided,
            the scopes given to the client will be used.

        Yields
        ------
        Session
            The created session. This is useful when managing multiple
            sessions.

        Examples
        --------
        >>> with client.session():
        ...     for year in range(2019, 2024):
        ...         client.fetch_report(
        ...             start_date=dt.date(year, 1, 1),
        ...             end_date=dt.date(year, 12, 31),
        ...         )
        """

        _log.debug("New client session created")
        self._session = self._create_session(key, tokens, scopes)
        yield self._session
        self._session = None

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
        session: Session | None = None,
        report_type: type[ReportType] | None = None,
        display_nested_exceptions: bool = False,
    ) -> "Report":
        """Fetch an analytics report.

        ??? note "Changed in version 6.0"
            You can now pass a session to this method. This is useful
            when managing multiple sessions.

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
        session
            The session to use for this request. This is useful when
            managing multiple sessions. If this is not provided, the
            client will either use an available session or create a
            default one.
        report_type
            The type of report this request is for. If this is not
            provided, analytix will validate across all report types.
            This is useful if you know what kind of report you want
            ahead of time, and don't want analytix to assume.
        display_nested_exceptions
            Whether to allow errors from multiple report types to be
            displayed at once. If this is `True`, analytix will display
            all errors from all report types with the fewest errors.
            Otherwise, it will only display errors from what it believes
            to be the best candidate. This is `False` by default as
            nested exception groups can look quite messy, but can lead
            to analytix making incorrect assumptions. If `report_type`
            is set, this is ignored.

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
        session = session or self._session or self._create_session()
        return ReportBuilder(
            dimensions=dimensions,
            filters=filters,
            metrics=metrics,
            sort_options=sort_options,
            max_results=max_results,
            start_date=start_date,
            end_date=end_date,
            currency=currency,
            start_index=start_index,
            include_historical_data=include_historical_data,
            display_nested_exceptions=display_nested_exceptions,
        ).build(report_type_cls=report_type, session=session)

    def fetch_groups(
        self,
        *,
        ids: Collection[str] | None = None,
        next_page_token: str | None = None,
        session: Session | None = None,
    ) -> "GroupList":
        """Fetch a list of analytics groups.

        ??? note "Changed in version 6.0"
            You can now pass a session to this method. This is useful
            when managing multiple sessions.

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
        session
            The session to use for this request. This is useful when
            managing multiple sessions. If this is not provided, the
            client will either use an available session or create a
            default one.

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
        session = session or self._session or self._create_session()
        query = GroupQuery(ids, next_page_token)
        with self._request(query.url, token=session.access_token) as resp:
            return GroupList.from_json(self, json.loads(resp.data))

    def fetch_group_items(
        self,
        group_id: str,
        session: Session | None = None,
    ) -> "GroupItemList":
        """Fetch a list of all items within a group.

        ??? note "Changed in version 6.0"
            You can now pass a session to this method. This is useful
            when managing multiple sessions.

        Parameters
        ----------
        group_id
            The ID of the group to fetch items for.

        Other Parameters
        ----------------
        session
            The session to use for this request. This is useful when
            managing multiple sessions. If this is not provided, the
            client will either use an available session or create a
            default one.

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
        session = session or self._session or self._create_session()
        query = GroupItemQuery(group_id)
        with self._request(query.url, token=session.access_token) as resp:
            return GroupItemList.from_json(json.loads(resp.data))
