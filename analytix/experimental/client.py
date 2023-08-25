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

from analytix.errors import APIError, AuthorisationError
from analytix.experimental import auth
from analytix.experimental.auth import Secrets, Tokens
from analytix.experimental.mixins import RequestMixin
from analytix.experimental.shard import Shard
from analytix.experimental.types import PathLike
from analytix.oidc import Scopes

if TYPE_CHECKING:
    from analytix.groups import GroupItemList, GroupList
    from analytix.reports import AnalyticsReport

_log = logging.getLogger(__name__)


class BaseClient(RequestMixin, metaclass=ABCMeta):
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
        raise NotImplementedError

    def token_refresh_required(self, access_token: str) -> bool:
        try:
            with self._request(auth.OAUTH_CHECK_URL + access_token, post=True):
                _log.debug("Access token does not need refreshing")
                return False
        except APIError:
            _log.debug("Access token needs refreshing")
            return False

    def refresh_access_token(self, tokens: Tokens) -> Optional[Tokens]:
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
    def shard(self, tokens: Tokens) -> Generator[Shard, None, None]:
        shard = Shard(self._scopes, tokens)
        yield shard
        del shard


class Client(BaseClient):
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
        self._tokens_file = Path(tokens_file)
        self._ws_port = ws_port
        self._auto_open_browser = not in_wsl() if auto_open_browser is None else True

    def __enter__(self) -> "Client":
        return self

    def authorise(self, *, force_refresh: bool = False) -> Tokens:
        if self._tokens_file.is_file():
            tokens = Tokens.load_from(self._tokens_file)
            if refreshed := self.refresh_access_token(tokens, force=force_refresh):
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
        if not force and not self.token_refresh_required(tokens.access_token):
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
    ) -> "AnalyticsReport":
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
        tokens = self.authorise(**kwargs)
        with self.shard(tokens) as shard:
            return shard.fetch_groups(ids=ids, next_page_token=next_page_token)

    def fetch_group_items(self, group_id: str, **kwargs: Any) -> "GroupItemList":
        tokens = self.authorise(**kwargs)
        with self.shard(tokens) as shard:
            return shard.fetch_group_items(group_id)
