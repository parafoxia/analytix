# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

__all__ = (
    "Client",
    "Scopes",
    "can_use",
    "enable_logging",
    "groups",
    "process_path",
    "reports",
)

__productname__ = "analytix"
__version__ = "6.0.0a2"
__description__ = "A simple yet powerful SDK for the YouTube Analytics API."
__url__ = "https://github.com/parafoxia/analytix"
__docs__ = "https://parafoxia.github.io/analytix"
__author__ = "Ethan Henderson"
__author_email__ = "ethan.henderson.1998@gmail.com"
__license__ = "BSD 3-Clause 'New' or 'Revised' License"
__bugtracker__ = "https://github.com/parafoxia/analytix/issues"
__ci__ = "https://github.com/parafoxia/analytix/actions"
__changelog__ = "https://github.com/parafoxia/analytix/releases"

from . import groups
from . import reports
from .auth import Scopes
from .client import Client
from .utils import can_use
from .utils import process_path
from .ux import enable_logging
