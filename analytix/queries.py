# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

__all__ = ("GroupItemQuery", "GroupQuery")

import logging
from collections.abc import Collection

API_BASE_URL = "https://youtubeanalytics.googleapis.com/v2"
API_REPORTS_URL = f"{API_BASE_URL}/reports"
API_GROUPS_URL = f"{API_BASE_URL}/groups"
API_GROUP_ITEMS_URL = f"{API_BASE_URL}/groupItems"

_log = logging.getLogger(__name__)


class GroupQuery:
    __slots__ = ("ids", "next_page_token")

    def __init__(
        self,
        ids: Collection[str] | None = None,
        next_page_token: str | None = None,
    ) -> None:
        self.ids = ids or ()
        self.next_page_token = next_page_token

    @property
    def url(self) -> str:
        ids = ("id=" + ",".join(self.ids)) if self.ids else "mine=true"
        npt = f"&next_page_token={self.next_page_token}" if self.next_page_token else ""
        return f"{API_GROUPS_URL}?{ids}{npt}"


class GroupItemQuery:
    __slots__ = ("group_id",)

    def __init__(self, group_id: str) -> None:
        self.group_id = group_id

    @property
    def url(self) -> str:
        return f"{API_GROUP_ITEMS_URL}?groupId={self.group_id}"
