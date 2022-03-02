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

import datetime as dt
import logging
import os
import pathlib
import typing as t

import httpx

import analytix
from analytix import errors, oauth
from analytix.queries import Query
from analytix.reports import Report
from analytix.secrets import Secrets
from analytix.tokens import Tokens

log = logging.getLogger(__name__)


class Analytics:
    def __init__(self, secrets: Secrets, **kwargs: t.Any) -> None:
        self.secrets = secrets
        self._session = httpx.Client(**kwargs)
        self._tokens: Tokens | None = None

    def __str__(self) -> str:
        return self.secrets.project_id

    @classmethod
    def with_secrets(cls, path: pathlib.Path | str) -> Analytics:
        if not os.path.isfile(path):
            raise FileNotFoundError("you must provided a valid path to a secrets file")

        return cls(Secrets.from_file(path))

    @property
    def authorised(self) -> bool:
        return self._tokens is not None

    def close_session(self) -> None:
        self._session.close()
        log.info("Session closed")

    def _try_load_tokens(self, path: pathlib.Path) -> Tokens | None:
        if not path.is_file():
            return None

        return Tokens.from_file(path)

    def _retrieve_tokens(self) -> Tokens:
        url, state = oauth.auth_url_and_state(self.secrets)
        code = input(f"{url}\nEnter code > ")
        data, headers = oauth.access_data_and_headers(code, self.secrets)

        r = self._session.post(self.secrets.token_uri, data=data, headers=headers)
        r.raise_for_status()
        return Tokens.from_data(r.json())

    def needs_refresh(self) -> bool:
        if not self._tokens:
            return False

        log.debug("Checking if token needs to be refreshed...")
        r = self._session.get(analytix.OAUTH_CHECK_URL + self._tokens.access_token)
        if r.is_error:
            # This seems to fail sometimes when a token is invalid, so
            # just refresh it -- we probably need to anyways.
            return True

        # If it's only got a few minutes on it, might as well refresh.
        return int(r.json().get("expires_in", 0)) < 300

    def refresh_access_token(self) -> None:
        if not self._tokens:
            log.warning("There are no tokens to refresh")
            return

        log.info("Refreshing access token...")
        data, headers = oauth.refresh_data_and_headers(
            self._tokens.refresh_token, self.secrets
        )

        r = self._session.post(self.secrets.token_uri, data=data, headers=headers)
        r.raise_for_status()
        self._tokens.update(r.json())
        self._tokens.write(self._token_path)

    def authorise(
        self, *, token_path: pathlib.Path | str = ".", force: bool = False
    ) -> Tokens:
        if not isinstance(token_path, pathlib.Path):
            token_path = pathlib.Path(token_path)

        if token_path.is_dir():
            token_path = token_path / "tokens.json"

        self._token_path = token_path

        if not force:
            log.info("Attempting to load tokens...")
            self._tokens = self._try_load_tokens(token_path)

        if not self._tokens:
            log.info("Unable to load tokens; you will need to authorise")
            self._tokens = self._retrieve_tokens()
            self._tokens.write(token_path)

        log.info("Authorisation complete!")
        return self._tokens

    def retrieve(
        self,
        *,
        dimensions: t.Collection[str] | None = None,
        filters: dict[str, str] | None = None,
        metrics: t.Collection[str] | None = None,
        sort_options: t.Collection[str] | None = None,
        max_results: int = 0,
        start_date: dt.date | None = None,
        end_date: dt.date | None = None,
        currency: str = "USD",
        start_index: int = 1,
        include_historical_data: bool = False,
        skip_validation: bool = False,
    ) -> Report:
        query = Query(
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

        if not skip_validation:
            query.validate()
        else:
            log.warning("Skipping validation")

        if not self.authorised:
            self.authorise()

        try:
            if self.needs_refresh():
                self.refresh_access_token()
        except httpx.HTTPStatusError:
            log.warning(
                "Token could not be refreshed due to an unexpected error; analytix "
                "will continue for now, but you may need to manually reset your tokens"
            )

        assert self._tokens is not None
        headers = {"Authorization": f"Bearer {self._tokens.access_token}"}
        resp = self._session.get(query.url, headers=headers)
        data = resp.json()
        log.debug(f"Data retrieved: {data}")

        if next(iter(data)) == "error":
            error = data["error"]
            raise errors.APIError(error["code"], error["message"])

        assert query.rtype is not None
        report = Report(data, query.rtype)
        log.info(f"Created report of shape {report.shape}!")
        return report
