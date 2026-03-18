# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

__all__ = ("RequestMixin",)

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from urllib.parse import urlencode

import urllib3
from urllib3.exceptions import MaxRetryError

from analytix.errors import APIError
from analytix.errors import BadRequest
from analytix.errors import Forbidden
from analytix.errors import NotFound
from analytix.errors import Unauthorised

try:
    from urllib3 import BaseHTTPResponse as HTTPResponse
except ImportError:
    # urllib3 < 2.0 doesn't have the BaseHTTPResponse, so this is
    # done for compatibility with older versions.
    from urllib3 import HTTPResponse

ERROR_MAPPING = {
    400: BadRequest,
    401: Unauthorised,
    403: Forbidden,
    404: NotFound,
}

http = urllib3.PoolManager()


class RequestMixin:
    __slots__ = ()

    @contextmanager
    def _request(
        self,
        url: str,
        *,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        post: bool = False,
        ignore_errors: bool = False,
        token: str | None = None,
        timeout: float | None = None,
    ) -> Generator[HTTPResponse, None, None]:
        method = "POST" if post or data else "GET"
        headers = headers or {}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            resp = http.request(
                method,
                url,
                body=urlencode(data or {}),
                headers=headers,
                timeout=timeout,
            )
        except MaxRetryError as exc:
            if not ignore_errors:
                raise exc

            # Mock a 503 response that can be returned in the event of
            # an ignored timeout failure.
            resp = HTTPResponse(
                status=503,
                version=11,
                version_string="HTTP/1.1",
                reason=None,
                decode_content=False,
                request_url=url,
            )

        if resp.status > 399 and not ignore_errors:
            if resp.status == 403 and "/v2/reports" in url and resp.reason:
                resp.reason += " (probably misconfigured scopes)"

            raise ERROR_MAPPING.get(resp.status, APIError)(
                resp.status,
                resp.reason or "An error occurred",
            )

        yield resp
