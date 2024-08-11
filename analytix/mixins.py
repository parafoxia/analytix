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

__all__ = ("RequestMixin",)

from contextlib import contextmanager
from typing import Any
from typing import Dict
from typing import Generator
from typing import Optional
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
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        post: bool = False,
        ignore_errors: bool = False,
        token: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Generator["HTTPResponse", None, None]:
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
