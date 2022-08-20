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

from __future__ import annotations

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
    def authorised(self) -> bool:
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
        print(f"You need to authorise analytix. To do so, visit this URL: {url}")

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
        if not self._tokens:
            # Can't refresh if they're non-existent.
            return False

        _log.debug("Checking if access token needs to be refreshed...")
        resp = rq.get(analytix.OAUTH_CHECK_URL + self._tokens.access_token)
        return not resp.ok

    def refresh_access_token(self) -> None:
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

        if not self.authorised or force_authorisation:
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
        if not skip_update_check and not self._update_checked:
            if self.can_update():
                _log.warning("You do not have the latest stable version of analytix")

        if not self.authorised or force_authorisation:
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
        if not skip_update_check and not self._update_checked:
            if self.can_update():
                _log.warning("You do not have the latest stable version of analytix")

        if not self.authorised or force_authorisation:
            self.authorise()

        if self.needs_token_refresh():
            self.refresh_access_token()

        query = GroupItemQuery(group_id)
        return GroupItemList.from_json(self._request(query.url))
