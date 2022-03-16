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

__all__ = (
    "API_BASE_URL",
    "API_SCOPES",
    "Analytics",
    "AsyncAnalytics",
    "can_use",
    "OAUTH_CHECK_URL",
    "setup_logging",
)

__productname__ = "analytix"
__version__ = "3.0.1"
__description__ = "A simple yet powerful wrapper for the YouTube Analytics API."
__url__ = "https://github.com/parafoxia/analytix"
__docs__ = "https://analytix.readthedocs.io"
__author__ = "Ethan Henderson"
__author_email__ = "ethan.henderson.1998@gmail.com"
__license__ = "BSD 3-Clause 'New' or 'Revised' License"
__bugtracker__ = "https://github.com/parafoxia/analytix/issues"
__ci__ = "https://github.com/parafoxia/analytix/actions"
__changelog__ = "https://github.com/parafoxia/analytix/releases"

import typing as t

from pkg_resources import working_set


def can_use(cmpfunc: t.Callable[[t.Iterable[object]], bool], *libs: str) -> bool:
    """Whether a given library or module can be used. If multiple
    libraries are given, this returns ``True`` if they can *all* be
    used.

    Args:
        cmpfunc:
            The comparison function to use. Must be :obj:`all` or
            :obj:`any`.
        *libs:
            A series of libraries to check the availability for.

    Returns:
        Whether the check succeeded.
    """

    if cmpfunc not in (all, any):
        raise ValueError("comparison function must be 'all' or 'any'")

    ws = [p.key for p in working_set]
    return cmpfunc(l in ws for l in libs)


API_BASE_URL = "https://youtubeanalytics.googleapis.com/v2/reports?"
API_SCOPES = (
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
)
OAUTH_CHECK_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo?access_token="
UPDATE_CHECK_URL = "https://pypi.org/pypi/analytix/json"

from .analytics import Analytics
from .async_analytics import AsyncAnalytics
from .ux import setup_logging
