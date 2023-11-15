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

There are two clients to choose from:

* The base client (`BaseClient`)
* The scripting client (`Client`)

The scripting client is the simpler of the two to use and is designed
for use in scripts. Client authorisation and shard management is handled
for you, allowing you to focus on the data you wish to fetch.

The base client needs to be subclassed, and is designed for use in web
applications. It needs to be told how to authorise itself to best suit
your workflow, and requires you to create and destroy shards yourself.

You may wish to use the base client if:

* you're running your application on a server
* you want control over how your applications is authorised
* you want to store tokens in a database
* you need access to JWT ID tokens
"""

__all__ = ("BaseClient", "Client")

import datetime as dt
import json
import logging
import platform
import webbrowser
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Collection, Dict, Generator, Optional

from analytix import auth
from analytix.auth import Scopes, Secrets, Tokens
from analytix.errors import APIError, AuthorisationError
from analytix.mixins import RequestMixin
from analytix.shard import Shard
from analytix.types import PathLike

if TYPE_CHECKING:
    from analytix.groups import GroupItemList, GroupList
    from analytix.reports import Report

_log = logging.getLogger(__name__)


class BaseClient(RequestMixin, metaclass=ABCMeta):
    """A base client designed to be subclassed for use in web
    applications.

    This client provides an interface for retrieving reports and group
    data from the YouTube Analytics API, but requires you to implement
    your own authorisation routine. It also requires you to manually
    create and manage analytix "shards", though utilities are available
    to help with that.

    This will work as a context manager.

    Parameters
    ----------
    secrets_file
        The path to your secrets file.
    scopes
        The scopes to allow in requests. This is used to control whether
        or not to allow access to monetary data. If this is not
        provided, monetary data will not be accessible.

    !!! note "New in version 5.0"

    ??? example
        ```py
        from analytix import BaseClient

        class CustomClient(BaseClient):
            ...

        client = CustomClient("secrets.json")
        ```

    ??? example "Providing custom scopes"
        ```py
        from analytix import BaseClient, Scopes

        class CustomClient(BaseClient):
            ...

        client = CustomClient("secrets.json", scopes=Scopes.ALL)
        ```
    """

    __slots__ = ("_secrets", "_scopes")

    def __init__(
        self, secrets_file: PathLike, *, scopes: Scopes = Scopes.READONLY
    ) -> None:
        self._secrets = Secrets.load_from(Path(secrets_file))
        self._scopes = scopes

    def __enter__(self) -> "BaseClient":
        return self

    def __exit__(self, *_: Any) -> None:
        ...

    @abstractmethod
    def authorise(self) -> Tokens:
        """An abstract method used to authorise the client.

        The `BaseClient` requires you to overload this method when
        subclassing to suit your application's needs. Your
        implementation of this method must return a `Tokens` object.

        Returns
        -------
        Tokens
            Your tokens.

        Raises
        ------
        NotImplementedError
            You called this method without overloading it.

        !!! info "See also"
            You may find the `analytix.auth.auth_uri` and `.token_uri`
            functions helpful when writing your custom implementation.
        """
        raise NotImplementedError

    def token_is_valid(self, access_token: str) -> bool:
        """A helper method to check whether your access token is valid.

        The default implementation makes a call to Google's OAuth2 API
        to determine the token's validity.

        Parameters
        ----------
        access_token
            Your access token.

        Returns
        -------
        bool
            Whether the token is valid or not. If it isn't, it needs
            refreshing.

        !!! note "New in version 5.0"

        ??? example
            ```py
            >>> client.token_is_valid("1234567890")
            True
            ```
        """
        try:
            with self._request(auth.OAUTH_CHECK_URL + access_token, post=True):
                _log.debug("Access token does not need refreshing")
                return True
        except APIError:
            _log.debug("Access token needs refreshing")
            return False

    def scopes_are_sufficient(self, scopes: str) -> bool:
        """A helper method to check whether your stored scopes are
        sufficient.

        This cross-checks the scopes you provided the client with the
        scopes your tokens are authorised with and determines whether
        your tokens provide enough access.

        This is not an equality check; if your tokens are authorised
        with all scopes, but you only passed the READONLY scope to the
        client, this will return `True`.

        Parameters
        ----------
        scopes
            Your stored scopes. These are the scopes in your tokens, not
            the ones you passed to the client.

        Returns
        -------
        bool
            Whether the scopes are sufficient or not. If they're not,
            you'll need to reauthorise.

        !!! note "New in version 5.0"

        ??? example
            ```py
            # Yes, it's `.scope`, not `.scopes`.
            >>> client.scopes_are_sufficient(tokens.scope)
            True
            ```
        """
        # The <= here means "is LHS a subset of RHS?".
        sufficient = set(self._scopes.value.split(" ")) <= set(scopes.split(" "))
        _log.debug(f"Stored scopes are {'' if sufficient else 'in'}sufficient")
        return sufficient

    def refresh_access_token(self, tokens: Tokens) -> Optional[Tokens]:
        """Refresh your access token.

        While this method should always be sufficient to refresh your
        access token, the default implementation does not save new
        tokens anywhere. If this is something you need, you will need
        to extend this method to accommodate that.

        Parameters
        ----------
        tokens
            Your tokens.

        Returns
        -------
        Tokens or None
            Your refreshed tokens, or `None` if they could not be
            refreshed. In the latter instance, your client will need to
            be reauthorised from scratch.

        !!! note "Changed in version 5.0"
            This is now handled by the client rather than by individual
            shards.

        ??? example
            ```py
            >>> client.refresh_access_token(tokens)
            Tokens(access_token="1234567890", ...)
            ```
        """
        refresh_token = tokens.refresh_token
        refresh_uri, data, headers = auth.refresh_uri(self._secrets, refresh_token)

        _log.debug("Refreshing access token")
        with self._request(
            refresh_uri, data=data, headers=headers, ignore_errors=True
        ) as resp:
            if resp.status > 399:
                _log.debug("Access token could not be refreshed")
                return None

            _log.debug("Access token has been refreshed successfully")
            return tokens.refresh(resp.data)

    @contextmanager
    def shard(
        self, tokens: Tokens, *, scopes: Optional[Scopes] = None
    ) -> Generator[Shard, None, None]:
        """A context manager for creating shards.

        You can think of shards as mini-clients, each able to make
        requests using their own tokens. This allows you to accommodate
        the needs of multiple users, or even allow a single user to make
        multiple requests, without having to call your authorisation
        routine multiple times.

        Generally, shards should only live for a single request or
        a batch of related requests.

        Parameters
        ----------
        tokens
            Your tokens.
        scopes
            The scopes to allow in requests. If this is not provided,
            the shard will inherit the client's scopes.

        Yields
        ------
        Shard
            A new shard. It will be destroyed upon exiting the context
            manager.

        !!! note "Changed in version 5.0"
            You can now provide custom scopes for shards.

        ??? example
            ```py
            tokens = client.authorise()
            with client.shard(tokens) as shard:
                shard.fetch_report()
            ```

        ??? example "Providing custom scopes"
            ```py
            from analytix import Scopes

            tokens = client.authorise()
            with client.shard(tokens, scopes=Scopes.ALL) as shard:
                shard.fetch_groups()
            ```
        """
        shard = Shard(scopes or self._scopes, tokens)
        yield shard
        del shard


class Client(BaseClient):
    """A fully-functional client designed for use in scripts.

    Unlike the `BaseClient`, this client is capable of authorising
    itself and provides helper methods to abstract shard management away
    from you.

    This will work as a context manager.

    Parameters
    ----------
    secrets_file
        The path to your secrets file.
    scopes
        The scopes to allow in requests. This is used to control whether
        or not to allow access to monetary data. If this is not
        provided, monetary data will not be accessible.
    tokens_file
        The path to save your tokens to. This must be a JSON file, but
        does not need to exist. If this is not provided, your tokens
        will be saved to a file called "tokens.json" in your current
        working directory.
    ws_port
        The port the client's webserver will use during authorisation.
    auto_open_browser
        Whether to automatically open a new browser tab when
        authorising. If this is `False`, a link will be output to the
        console instead. If this is not provided, its value will be set
        based on your operating system; it will be set to `False` if you
        use WSL, and `True` otherwise.

    Raises
    ------
    ValueError
        `tokens_file` is not a JSON file.

    !!! note "Changed in version 5.0"
        * You should now provide a tokens file rather than a tokens
          directory
        * `auto_open_browser` is now set based on your OS by default
        * Monetary data is now no longer accessible by default
    """

    def __init__(
        self,
        secrets_file: PathLike,
        *,
        scopes: Scopes = Scopes.READONLY,
        tokens_file: PathLike = "tokens.json",
        ws_port: int = 8080,
        auto_open_browser: Optional[bool] = None,
    ) -> None:
        def in_wsl() -> bool:
            return "microsoft-standard" in platform.uname().release

        super().__init__(secrets_file, scopes=scopes)
        self._ws_port = ws_port
        self._auto_open_browser = not in_wsl() if auto_open_browser is None else True

        self._tokens_file = Path(tokens_file)
        if self._tokens_file.suffix != ".json":
            raise ValueError("tokens file must be a JSON file")

    def __enter__(self) -> "Client":
        return self

    def authorise(self, *, force_refresh: bool = False) -> Tokens:
        """Authorise the client.

        This method always does the minimum possible work necessary to
        authorise the client. This means that stored tokens will be
        prioritised, and the full auth flow will only trigger when
        necessary. Token refreshing is handled automatically.

        Client methods authorise the client for you, so you don't need
        to call this manually when using those. If you plan to make
        multiple requests in a row using the same client, it's better to
        call this manually and create a shard with the generated tokens
        to avoid authorising the client multiple times.

        Parameters
        ----------
        force_refresh
            Whether to forcibly refresh your access token, even if the
            token is still valid.

        Returns
        -------
        Tokens
            Your tokens.

        Raises
        ------
        RuntimeError
            The client attempted to open a new browser tab, but failed.
        AuthorisationError
            Something went wrong during authorisation.

        !!! note
            You will only need to call this method directly if you plan
            to create shards yourself.

        !!! note "Changed in version 5.0"
            * You can no longer pass a filename to load a specific set
              of tokens — you must create a new client for each channel
              you wish to fetch data for
            * You can now forcibly refresh access tokens using the
              provided keyword argument

        ??? example
            ```py
            >>> client.authorise()
            Tokens(access_token="1234567890", ...)
            ```
        """
        if self._tokens_file.is_file():
            tokens = Tokens.load_from(self._tokens_file)
            if self.scopes_are_sufficient(tokens.scope) and (
                refreshed := self.refresh_access_token(tokens, force=force_refresh)
            ):
                _log.info("Existing tokens are valid -- no authorisation necessary")
                return refreshed

        _log.info("Authorisation necessary -- starting authorisation flow")

        auth_uri, params, _ = auth.auth_uri(self._secrets, self._scopes, self._ws_port)
        if self._auto_open_browser:
            if not webbrowser.open(auth_uri, 0, True):
                raise RuntimeError("web browser failed to open")
        else:
            print(  # noqa: T201
                "\33[38;5;45mYou need to authorise analytix.\33[0m "
                f"\33[4m{auth_uri}\33[0m"
            )

        code = auth.run_flow(params)
        _log.debug("Authorisation code: %s", code)
        token_uri, data, headers = auth.token_uri(
            self._secrets, code, params["redirect_uri"]
        )

        with self._request(token_uri, data=data, headers=headers) as resp:
            if resp.status > 399:
                error = json.loads(resp.data)
                raise AuthorisationError(
                    f"could not authorise: {error['error_description']} "
                    f"({error['error']})"
                )

            tokens = Tokens.from_json(resp.data)

        tokens.save_to(self._tokens_file)
        _log.info("Authorisation complete!")
        return tokens

    def refresh_access_token(
        self, tokens: Tokens, *, force: bool = False
    ) -> Optional[Tokens]:
        """Refresh your access token.

        Parameters
        ----------
        tokens
            Your tokens.
        force
            Whether to forcibly refresh your access token, even if the
            token is still valid.

        Returns
        -------
        Tokens or None
            Your refreshed tokens, or `None` if they could not be
            refreshed.

        !!! note
            This method should never need to be called, as the
            `authorise` method will call it automatically when
            necessary.

        !!! note "New in version 5.0"
        """
        if not force and self.token_is_valid(tokens.access_token):
            return tokens

        if refreshed := super().refresh_access_token(tokens):
            refreshed.save_to(self._tokens_file)

        return refreshed

    def fetch_report(
        self,
        *,
        dimensions: Optional[Collection[str]] = None,
        filters: Optional[Dict[str, str]] = None,
        metrics: Optional[Collection[str]] = None,
        start_date: Optional[dt.date] = None,
        end_date: Optional[dt.date] = None,
        sort_options: Optional[Collection[str]] = None,
        max_results: int = 0,
        currency: str = "USD",
        start_index: int = 1,
        include_historical_data: bool = False,
        **kwargs: Any,
    ) -> "Report":
        """Authorise the client and fetch an analytics report.

        This gets video reports by default. To get playlist reports, you
        must set the `"isCurated"` filter to `"1"`.

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

        Returns
        -------
        Report
            The generated report.

        Other Parameters
        ----------------
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
        **kwargs
            Additional keyword arguments to be passed to the `authorise`
            method.

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
        RuntimeError
            The client attempted to open a new browser tab, but failed.
        AuthorisationError
            Something went wrong during authorisation.

        !!! warning
            If your channel is not partnered, attempting to access
            monetary data will result in a `Forbidden` error. Ensure
            your scopes are set up correctly before calling this method.

        !!! info "See also"
            You can learn more about dimensions, filters, metrics, and
            sort options by reading the [detailed guides](../../guides/
            dimensions).

        !!! note "Changed in version 5.0"
            This used to be `retrieve_report`.

        ??? example "Fetching daily analytics data for 2022"
            ```py
            from datetime import datetime

            shard.fetch_report(
                dimensions=("day",),
                start_date=datetime.date(2022, 1, 1),
                end_date=datetime.date(2022, 12, 31),
            )
            ```

        ??? example "Fetching 10 most watched videos over last 28 days"
            ```py
            shard.fetch_report(
                dimensions=("video",),
                metrics=("estimatedMinutesWatched", "views"),
                sort_options=("-estimatedMinutesWatched"),
                max_results=10,
            )
            ```

        ??? example "Fetching playlist analytics"
            ```py
            shard.fetch_report(filters={"isCurated": "1"})
            ```
        """
        tokens = self.authorise(**kwargs)
        with self.shard(tokens) as shard:
            return shard.fetch_report(
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

    def fetch_groups(
        self,
        *,
        ids: Optional[Collection[str]] = None,
        next_page_token: Optional[str] = None,
        **kwargs: Any,
    ) -> "GroupList":
        """Authorise the client and fetch a list of analytics groups.

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
        **kwargs
            Additional keyword arguments to be passed to the `authorise`
            method.

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

        !!! note "Changed in version 5.0"
            You can now pass a series of keyword arguments to be passed
            on to the `authorise` method.
        """
        tokens = self.authorise(**kwargs)
        with self.shard(tokens) as shard:
            return shard.fetch_groups(ids=ids, next_page_token=next_page_token)

    def fetch_group_items(self, group_id: str, **kwargs: Any) -> "GroupItemList":
        """Authorise the client and fetch a list of all items within a
        group.

        Parameters
        ----------
        group_id
            The ID of the group to fetch items for.
        **kwargs
            Additional keyword arguments to be passed to the `authorise`
            method.

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

        !!! note "Changed in version 5.0"
            You can now pass a series of keyword arguments to be passed
            on to the `authorise` method.
        """
        tokens = self.authorise(**kwargs)
        with self.shard(tokens) as shard:
            return shard.fetch_group_items(group_id)
