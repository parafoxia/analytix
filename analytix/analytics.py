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
    """A class representing a client for the YouTube Analytics API.

    Args:
        secrets:
            The project secrets from the Google Developers Console.

    Keyword Args:
        **kwargs:
            Additional parameters to be passed to the
            :obj:`httpx.Client` constructor.
    """

    __slots__ = ("secrets", "_session", "_tokens", "_token_path", "_checked_for_update")

    def __init__(self, secrets: Secrets, **kwargs: t.Any) -> None:
        self.secrets = secrets
        self._session = httpx.Client(**kwargs)
        self._tokens: Tokens | None = None
        self._token_path = pathlib.Path()
        self._checked_for_update = False

    def __str__(self) -> str:
        return self.secrets.project_id

    @classmethod
    def with_secrets(cls, path: pathlib.Path | str) -> Analytics:
        """Create a client using secrets from a file downloaded from the
        Google Developers Console.

        Args:
            path:
                The path to the secrets file.

        Returns:
            The created client instance.
        """

        if not os.path.isfile(path):
            raise FileNotFoundError("you must provided a valid path to a secrets file")

        return cls(Secrets.from_file(path))

    @property
    def authorised(self) -> bool:
        """Whether this client is authorised."""

        return self._tokens is not None

    def close_session(self) -> None:
        """Close the currently open session."""

        self._session.close()
        log.info("Session closed")

    def check_for_updates(self) -> str | None:
        """Checks for newer versions of analytix.

        Returns:
            The latest version, or ``None`` if either you are using the
            latest version, or the latest version could not be
            ascertained.
        """

        log.debug("Checking for updates...")

        r = self._session.get(analytix.UPDATE_CHECK_URL)
        if r.is_error:
            # If we can't get the info, just ignore it.
            log.debug("Failed to get version information")
            return None

        latest = r.json()["info"]["version"]
        if analytix.__version__ != latest:
            log.warning(
                f"You do not have the latest stable version of analytix (v{latest})"
            )

        self._checked_for_update = True
        return t.cast(str, latest)

    def _try_load_tokens(self, path: pathlib.Path) -> Tokens | None:
        if not path.is_file():
            return None

        return Tokens.from_file(path)

    def _retrieve_tokens(self) -> Tokens:
        url, state = oauth.auth_url_and_state(self.secrets)
        code = input(f"{url}\nEnter code > ")
        data, headers = oauth.access_data_and_headers(code, self.secrets)

        r = self._session.post(self.secrets.token_uri, data=data, headers=headers)
        if r.is_error:
            error = r.json()["error"]
            raise errors.AuthenticationError(error["code"], error["message"])

        return Tokens.from_data(r.json())

    def needs_refresh(self) -> bool:
        """Check whether any existing token needs refreshing. If the
        client is not currently authorised, this will return ``False``.

        Returns:
            Whether the access token needs to be refreshed.
        """

        if not self._tokens:
            return False

        log.debug("Checking if token needs to be refreshed...")
        r = self._session.get(analytix.OAUTH_CHECK_URL + self._tokens.access_token)
        return r.is_error

    def refresh_access_token(self) -> None:
        """Refresh the access token."""

        if not self._tokens:
            log.warning("There are no tokens to refresh")
            return

        log.info("Refreshing access token...")
        data, headers = oauth.refresh_data_and_headers(
            self._tokens.refresh_token, self.secrets
        )

        r = self._session.post(self.secrets.token_uri, data=data, headers=headers)
        if not r.is_error:
            self._tokens.update(r.json())
        else:
            log.info("Your refresh token has expired; you will need to reauthorise")
            self._tokens = self._retrieve_tokens()

        self._tokens.write(self._token_path)

    def authorise(  # nosec B107
        self, token_path: pathlib.Path | str = ".", *, force: bool = False
    ) -> Tokens:
        """Authorise the client. This is called automatically when
        needed if not manually called, though if you want to authorise
        with non-default options, you will need to call this manually.

        Args:
            token_path:
                The path to the token file or the directory the token
                file is or should be stored in. If this is not provided,
                this defaults to the current directory, and if a
                directory is passed, the file is given the name
                "tokens.json".

        Keyword Args:
            force:
                Whether to forcibly authorise the client. Defaults to
                ``False``.

        Returns:
            The tokens the client is authorised with.
        """

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
        force_authorisation: bool = False,
        skip_update_check: bool = False,
        skip_refresh_check: bool = False,
        token_path: pathlib.Path | str = ".",
    ) -> Report:
        """Retrieves a report from the YouTube Analytics API.

        Keyword Args:
            dimensions:
                The dimensions to use in the report. Defaults to
                ``None``. If this is ``None``, no dimensions will be
                used.
            filters:
                The filters to use in the report. Defaults to ``None``.
                If this is ``None``, no filters will be used.
            metrics:
                The metrics to use in the report. Defaults to ``None``.
                If this is ``None``, all available metrics for the
                selected report type will be used.
            sort_options:
                The sort options to use in the report. Defaults to
                ``None``. If this is ``None``, no sort options will be
                used.
            max_results:
                The maximum number of results to include in the report.
                Defaults to ``0``. If this is ``0``, no limit will be
                set on the maximum number of results.
            start_date:
                The date from which to begin pulling data. Defaults to
                ``None``. If this is ``None``, this will be set to 28
                days before the end date.
            end_date:
                The date in which to pull data up to. Defaults to
                ``None``. If this is ``None``, this will be set to the
                current date.

                .. warning::
                    Due to the nature of the YouTube Analytics API, some
                    dates may be missing from the report. analytix does
                    not compensate for this, as the number missing is
                    not consistent.

            currency:
                The currency in which financial data will be displayed.
                Defaults to "USD". This **must** be an ISO 4217 currency
                code (such as USD or GBP).
            start_index:
                The first row of the data to include in the report.
                Defaults to ``1``. This value one-indexed, meaning
                setting this to ``1`` will include all rows, and
                setting it to ``10`` will remove the first nine rows.
            include_historical_data:
                Whether to retrieve data from dates earlier than the
                current channel owner assumed ownership of the channel.
                Defaults to ``False``. You only need to worry about this
                if you are not the original owner of the channel.
            skip_validation:
                Whether to skip the validation process. Defaults to
                ``False``.
            force_authorisation:
                Whether to force the (re)authorisation of the client.
                Defaults to ``False``.
            skip_update_check:
                Whether to skip checking for updates. Defaults to
                ``False``.
            skip_refresh_token:
                Whether to skip token refreshing. Defaults to ``False``.
            token_path:
                The path to the token file or the directory the token
                file is or should be stored in. If this is not provided,
                this defaults to the current directory, and if a
                directory is passed, the file is given the name
                "tokens.json".

                .. versionadded:: 3.3.0

        Returns:
            An instance for working with retrieved data.
        """

        if not skip_update_check and not self._checked_for_update:
            self.check_for_updates()

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
            log.warning(
                "Skipping validation -- invalid requests will count toward your quota"
            )

        if not self.authorised or force_authorisation:
            self.authorise(token_path=token_path, force=force_authorisation)

        if (not skip_refresh_check) and self.needs_refresh():
            self.refresh_access_token()

        assert self._tokens is not None
        headers = {"Authorization": f"Bearer {self._tokens.access_token}"}
        resp = self._session.get(query.url, headers=headers)
        data = resp.json()
        log.debug(f"Data retrieved: {data}")

        if next(iter(data)) == "error":
            error = data["error"]
            raise errors.APIError(error["code"], error["message"])

        if not query.rtype:
            query.set_report_type()

        assert query.rtype is not None
        report = Report(data, query.rtype)
        log.info(f"Created report of shape {report.shape}!")
        return report
