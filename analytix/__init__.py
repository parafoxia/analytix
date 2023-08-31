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
    "API_GROUPS_URL",
    "API_GROUP_ITEMS_URL",
    "API_REPORTS_URL",
    "BaseClient",
    "can_use",
    "Client",
    "enable_logging",
    "groups",
    "process_path",
    "reports",
    "Scopes",
    "UPDATE_CHECK_URL",
)

__productname__ = "analytix"
__version__ = "5.0.0rc1"
__description__ = "A simple yet powerful SDK for the YouTube Analytics API."
__url__ = "https://github.com/parafoxia/analytix"
__docs__ = "https://parafoxia.github.io/analytix"
__author__ = "Ethan Henderson"
__author_email__ = "ethan.henderson.1998@gmail.com"
__license__ = "BSD 3-Clause 'New' or 'Revised' License"
__bugtracker__ = "https://github.com/parafoxia/analytix/issues"
__ci__ = "https://github.com/parafoxia/analytix/actions"
__changelog__ = "https://github.com/parafoxia/analytix/releases"

API_BASE_URL = "https://youtubeanalytics.googleapis.com/v2"
API_REPORTS_URL = f"{API_BASE_URL}/reports?"
API_GROUPS_URL = f"{API_BASE_URL}/groups?"
API_GROUP_ITEMS_URL = f"{API_BASE_URL}/groupItems?"
UPDATE_CHECK_URL = "https://pypi.org/pypi/analytix/json"

from . import groups, reports
from .auth import Scopes
from .client import BaseClient, Client
from .utils import can_use, process_path
from .ux import enable_logging
