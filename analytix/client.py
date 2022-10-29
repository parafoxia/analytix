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

"""Client interfaces for analytix.

This module contains three clients:

* `AsyncBaseClient`
* `AsyncClient`
* `Client`

The first of these requires you to handle authorisation and shard
management yourself, and is designed for use in web applications. The
other two handle both authorisation and shard management for you, and
are designed for use in desktop applications.

You should only use the `AsyncBaseClient` if:

* you're running your application on a server
* you want control over how your application is authorised
* you want to store tokens in a database
* you need access to ID tokens

The `Client` provides a sync interface for analytix operations, which is
perfect if you are running simple scripts. This client acts as a wrapper
to the `AsyncClient` and is not a separate implementation. Because of
this, it is not threadsafe.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import sys
import typing as t
import webbrowser
from contextlib import contextmanager
from pathlib import Path
from types import TracebackType

from aiohttp import ClientSession

import analytix
from analytix import UPDATE_CHECK_URL, oidc
from analytix.errors import AuthorisationError, RefreshTokenExpired
from analytix.groups import GroupItemList, GroupList
from analytix.reports import AnalyticsReport
from analytix.shard import Shard

if t.TYPE_CHECKING:
    from analytix.types import OptionalPathLikeT, PathLikeT

_log = logging.getLogger(__name__)


class AsyncBaseClient:
    """A basic client interface for the YouTube Analytics API.

    This client provides methods for retrieving reports and group data
    from the YouTube Analytics API, but requires you to implement your
    own authorisation routine. It also requires you to perform shard
    management yourself, though utilities are available to help with
    that.

    Parameters
    ----------
    secrets_file : Path object or str
        The path to your secrets file.

    Other Parameters
    ----------------
    loop : AbstractEventLoop, optional
        The asyncio event loop to use. If this is not provided, the
        client will create one.
    session : ClientSession, optional
        The AIOHTTP client session to use. If this is not provided, the
        client will create one.

    !!! info "See also"
        If you want a client with self-authorising capabilities, see
        `AsyncClient`.

    ??? example "Basic example"
        ```py
        client = AsyncBaseClient("secrets.json")
        ```

    ??? example "Context manager example"
        ```py
        with AsyncBaseClient("secrets.json") as client:
            await client.teardown()
        ```
    """

    __slots__ = ("_loop", "_secrets", "_session")

    def __init__(
        self,
        secrets_file: PathLikeT,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        session: ClientSession | None = None,
        **kwargs: t.Any,
    ) -> None:
        try:
            self._loop = loop or asyncio.get_running_loop()
        except RuntimeError:
            self._loop = (
                asyncio.new_event_loop()
                if sys.version_info >= (3, 10)
                else asyncio.get_event_loop()
            )

        self._secrets = oidc.Secrets.from_file(secrets_file)
        self._session = session or ClientSession(loop=self._loop, **kwargs)

        self._loop.create_task(self._check_for_updates())

    def __str__(self) -> str:
        return self._secrets.project_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(project_id={self._secrets.project_id})"

    async def __aenter__(self) -> AsyncBaseClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.teardown()

    async def _check_for_updates(self) -> None:
        _log.debug("Checking for updates")

        async with self._session.get(UPDATE_CHECK_URL) as resp:
            if not resp.ok:
                # If we can't get the info, just ignore it.
                _log.debug("Failed to get version information")
                return

            latest = (await resp.json())["info"]["version"]

        if analytix.__version__ != latest:
            _log.warning(
                f"You do not have the latest stable version of analytix (v{latest})"
            )

    async def teardown(self) -> None:
        """Tears the client down.

        This should be called before your program ends unless you're
        using the client in a context manager.

        Returns
        -------
        None

        ??? example
            ```py
            await client.teardown()
            ```
        """

        await self._session.close()

    @contextmanager
    def shard(self, tokens: oidc.Tokens | dict[str, str | int]) -> t.Iterator[Shard]:
        """A context manager inside which shard operations can be
        performed.

        As many shards as necessary can be spawned, each sharing the
        client's session and secrets, but using their own tokens. If
        you have multiple users using your application at once, one
        shard should be spawned for each user. The shard is destroyed
        upon exiting the context.

        Parameters
        ----------
        tokens : Tokens object or JSON
            The tokens the shard should use.

        Yields
        ------
        Shard
            The newly created shard instance to use.

        ??? example
            ```py
            # tokens = Tokens object or JSON dict
            with client.shard(tokens) as shard:
                # The shard object should be used to make requests.
                await shard.refresh_access_token()
                await shard.retrieve_report(dimensions=("day",))
            ```
        """

        if not isinstance(tokens, oidc.Tokens):
            tokens = oidc.Tokens.from_json(tokens)

        shard = Shard(self._session, self._secrets, tokens)
        yield shard
        del shard


class AsyncClient(AsyncBaseClient):
    """A client interface for the YouTube Analytics API.

    This client adds self-authorisation routines on top of the base
    client. This client is not suitable for web applications; use the
    `AsyncBaseClient` instead.

    Parameters
    ----------
    secrets_file : Path object or str
        The path to your secrets file.
    tokens_dir : Path object or str, optional
        The directory in which tokens should be stored. If this is not
        provided, the current working directory is used.
    ws_port : int, optional
        The webserver port to use when authenticating.
    auto_open_browser : bool, optional
        Whether to automatically open the browser for authentication
        when necessary. If this is `False`, the auth URI is printed to
        the console.

    Other Parameters
    ----------------
    loop : AbstractEventLoop, optional
        The asyncio event loop to use. If this is not provided, the
        client will create one.
    session : ClientSession, optional
        The AIOHTTP client session to use. If this is not provided, the
        client will create one.

    Raises
    ------
    NotADirectoryError
        The token directory passed is not, in fact, a directory.

    !!! warning
        If you use WSL, the browser may not open even if
        `auto_open_browser` is `True`.

        To fix the issue:

        1. install [WSLU](https://github.com/wslutilities/wslu)
        2. add `export BROWSER="wslview"` to your shell's rc file

    !!! info "See also"
        If you want to build a web application, see `AsyncBaseClient`.

    ??? example "Basic example"
        ```py
        client = AsyncClient("secrets.json")
        ```

    ??? example "Context manager example"
        ```py
        with AsyncClient("secrets.json") as client:
            await client.teardown()
        ```

    ??? example "Advanced example"
        ```py
        client = AsyncClient(
            "secrets.json",
            tokens_dir="./tokens",
            ws_port=9999,
            auto_open_browser=True,
        )
        ```
    """

    __slots__ = (
        "_tokens_dir",
        "_ws_port",
        "_auto_open_browser",
        "_active_tokens",
        "_shard",
    )

    def __init__(
        self,
        secrets_file: PathLikeT,
        *,
        tokens_dir: OptionalPathLikeT = ".",
        ws_port: int = 8080,
        auto_open_browser: bool = False,
        loop: asyncio.AbstractEventLoop | None = None,
        session: ClientSession | None = None,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(
            secrets_file,
            loop=loop,
            session=session,
            **kwargs,
        )

        if tokens_dir is not None:
            if not isinstance(tokens_dir, Path):
                tokens_dir = Path(tokens_dir)

            if tokens_dir.is_file():
                raise NotADirectoryError("the token directory must not be a file")

        self._tokens_dir = tokens_dir
        self._ws_port = ws_port
        self._auto_open_browser = auto_open_browser

        self._active_tokens: str | None = None
        self._shard: Shard | None = None

    @property
    def active_tokens(self) -> str | None:
        """Return the ID of the currently active tokens.

        Returns
        -------
        str
            The ID of the currently active tokens.
        """

        return self._active_tokens

    async def _get_existing_tokens(self, token_id: str | None) -> oidc.Tokens | None:
        if self._shard and (token_id == self._active_tokens):
            return self._shard._tokens

        if not self._tokens_dir:
            return None

        token_path = self._tokens_dir / f"{token_id}.json"
        if not token_path.exists():
            return None

        return await oidc.Tokens.from_file(token_path)

    async def authorise(self, token_id: str | None = None) -> None:
        """Authorise the client.

        If you only want to pull data for a single channel, you don't
        need to call this manually. If you want to pull data for
        multiple channels, you will need to call this manually each time
        you want to switch channel.

        This method always does the minimum possible work necessary to
        authorise the client. This means that active and loadable tokens
        will be prioritised, and the full auth flow will only trigger
        when necessary. Token refreshing is handled automatically.

        Parameters
        ----------
        token_id : str, optional
            The ID of the tokens you want to use. If you own multiple
            channels, each one will use a different set of tokens and
            thus a different token ID. This ID will be the filename the
            tokens are stored as. If this is not provided, the client
            will use the currently active tokens. If no there are no
            active tokens, the client will use the project ID as defined
            in the secrets file.

        Returns
        -------
        None

        Raises
        ------
        AuthorisationError
            The client could not be authorised.
        RuntimeError
            The client tried and failed to automatically open a web
            browser for authentication.

        ??? example "Basic example"
            ```py
            await client.authorise()
            ```

        ??? example "Selecting tokens"
            ```py
            await client.authorise("my-tokens")
            # later on...
            await client.authorise("my-other-tokens")
            ```
        """

        # Determine token ID.
        token_id = token_id or self._active_tokens or self._secrets.project_id
        tokens: oidc.Tokens | None = None
        tokens = await self._get_existing_tokens(token_id)

        # Handle existing tokens.
        if tokens:
            self._shard = Shard(self._session, self._secrets, tokens)

            try:
                refreshed = bool(await self._shard.refresh_access_token(check=True))
                if refreshed and self._tokens_dir:
                    await self._shard._tokens.write(
                        self._tokens_dir / f"{token_id}.json"
                    )
                self._active_tokens = token_id
                _log.info("Authorisation complete!")
                return

            except RefreshTokenExpired:
                _log.info("Refresh token expired or not present, starting auth flow")

        # If no valid tokens by this point, start auth flow.
        auth_uri, params = oidc.auth_uri(self._secrets, self._ws_port)
        _log.debug(f"Auth parameters: {params}")

        if self._auto_open_browser:
            # TODO: Write WSLU warning.
            _log.info(f"Opening browser at {self._secrets.auth_uri}?...")
            if not webbrowser.open(auth_uri, 0, True):
                raise RuntimeError(
                    "Web browser failed to open — if you use WSL, refer to the docs"
                )
        else:
            print(
                "\33[38;5;45mYou need to authorise analytix.\33[0m "
                f"\33[4m{auth_uri}\33[0m"
            )

        code = oidc.authenticate(params)
        _log.debug(f"Auth code: {code}")

        # Exchange auth code with access token.
        token_uri, data, headers = oidc.token_uri(self._secrets, code, params)
        _log.debug(f"Token data: {data} / Token headers: {headers}")

        async with self._session.post(token_uri, data=data, headers=headers) as resp:
            resp_data = await resp.json()
            _log.debug(f"Tokens: {resp_data}")

            if not resp.ok:
                raise AuthorisationError(
                    f"could not authorise: {resp_data['error_description']} "
                    f"({resp_data['error']})"
                )

        # Configure tokens using response data.
        tokens = oidc.Tokens.from_json(resp_data)
        self._shard = Shard(self._session, self._secrets, tokens)
        if self._tokens_dir:
            await tokens.write(self._tokens_dir / f"{token_id}.json")
        self._active_tokens = token_id

        _log.info("Authorisation complete!")

    async def retrieve_report(
        self,
        *,
        dimensions: t.Collection[str] | None = None,
        filters: dict[str, str] | None = None,
        metrics: t.Collection[str] | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        sort_options: t.Collection[str] | None = None,
        max_results: int = 0,
        currency: str = "USD",
        start_index: int = 1,
        include_historical_data: bool = False,
    ) -> AnalyticsReport:
        """Retrieves a report.

        If the client is not already authorised, it will try and
        authorise itself.

        Parameters
        ----------
        dimensions : Collection of str, optional
            The dimensions to use within the request.
        filters : Mapping of str-to-str, optional
            The filters to use within the request.
        metrics : Collection of str, optional
            The metrics to use within the request. If none are provided,
            all available metrics are used.
        start_date : Date object
            The date in which data should be pulled from. If this is not
            provided, this is set to 28 days before the end date.
        end_date : Date object
            The date in which data should be pulled to. If this is not
            provided, this is set to the current date.

        Returns
        -------
        AnalyticsReport
            A instance of a report representation.

        Other Parameters
        ----------------
        sort_options : Collection of str, optional
            The sort options to use within the request.
        max_results : int, optional
            The maximum number of results the report should include. If
            this is `0`, no upper limit is applied.
        currency : str, optional
            The currency revenue data should be represented using. This
            should be an ISO 4217 currency code.
        start_index : int, optional
            The first row in the report to include. This is one-indexed.
            If this is `1`, all rows are included.
        include_historical_data : bool, optional
            Whether to include data from before the current channel
            owner assumed control of the channel. You only need to worry
            about this is the current channel owner did not create the
            channel.

        Raises
        ------
        APIError
            The YouTube Analytics API returned an error.
        AuthorisationError
            The client could not be authorised.
        InvalidRequest
            The request you wanted to make to the YouTube Analytics API
            was invalid.
        RuntimeError
            The client tried and failed to automatically open a web
            browser for authentication.

        !!! info "See also"
            You can learn more about dimensions, filters, metrics, and
            sort options by reading the [detailed guides](../../guides/
            dimensions).

        !!! important
            To get playlist reports, you must set the `"isCurated"`
            filter to `"1"`. View the playlist example to see how this
            is done.

        ??? example "Basic example"
            ```py
            # Fetch a report with the default settings.
            await client.retrieve_report()
            ```

        ??? example "Advanced example"
            ```py
            await client.retrieve_report(
                dimensions=("day", "subscribedStatus"),
                filters={"country": "GB"},
                metrics=("views", "likes", "comments"),
                start_date=datetime.date(2021, 1, 1),
                end_date=datetime.date(2021, 12, 31),
                sort_options=("-views",),
                max_results=100,
                currency="GBP",
                start_index=11,
                include_historical_data=True,
            )
            ```

        ??? example "Playlist example"
            ```py
            # This filter is required for playlist reports.
            await client.retrieve_report(filters={"isCurated": "1"})
            ```
        """

        await self.authorise()
        assert self._shard
        return await self._shard.retrieve_report(
            dimensions=dimensions,
            filters=filters,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date,
            sort_options=sort_options,
            max_results=max_results,
            currency=currency,
            start_index=start_index,
            include_historical_data=include_historical_data,
        )

    async def fetch_groups(
        self,
        *,
        ids: t.Collection[str] | None = None,
        next_page_token: str | None = None,
    ) -> GroupList:
        """Fetch the list of all your channel's groups.

        Parameters
        ----------
        ids : Collection of str, optional
            The IDs of groups you want to fetch. If none are provided,
            all your groups will be fetched.
        next_page_token : str, optional
            If you need to make multiple requests, you can pass this to
            load a specific page. To check if you've arrived back at the
            first page, check the next page token from the request and
            compare it to the next page token from the first page.

        Returns
        -------
        GroupList
            A instance of a group list representation.

        Raises
        ------
        APIError
            The YouTube Analytics API returned an error.
        AuthorisationError
            The client could not be authorised.
        RuntimeError
            The client tried and failed to automatically open a web
            browser for authentication.

        ??? example "Basic example"
            ```py
            >>> groups = await client.fetch_groups()
            >>> print(groups[0].id)
            "a1b2c3d4e5"
            ```
        """

        await self.authorise()
        assert self._shard
        return await self._shard.fetch_groups(ids=ids, next_page_token=next_page_token)

    async def fetch_group_items(self, group_id: str) -> GroupItemList:
        """Fetch the items of a specific group.

        Parameters
        ----------
        group_id : str
            The ID of the group you want to fetch the items of.

        Returns
        -------
        GroupItemsList
            A instance of a group items list representation.

        Raises
        ------
        APIError
            The YouTube Analytics API returned an error.
        AuthorisationError
            The client could not be authorised.
        RuntimeError
            The client tried and failed to automatically open a web
            browser for authentication.

        ??? example "Basic example"
            ```py
            # groups = response from client.fetch_groups()
            >>> group_items = await client.fetch_groups(groups[0].id)
            >>> print(group_items[0].id)
            "f6g7h8i9j0"
            ```
        """

        await self.authorise()
        assert self._shard
        return await self._shard.fetch_group_items(group_id)
