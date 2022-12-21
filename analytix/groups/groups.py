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

__all__ = ("Group", "GroupList", "GroupItem", "GroupItemList")

import datetime as dt
import typing as t
from dataclasses import dataclass

from dateutil.parser import parse as du_parse

if t.TYPE_CHECKING:
    from analytix.types import ResponseT


@dataclass(frozen=True)
class _Resource:
    __slots__ = ("kind", "etag")

    kind: str
    etag: str | None


@dataclass(frozen=True)
class Group(_Resource):
    __slots__ = ("id", "published_at", "title", "item_count", "item_type")

    id: str
    published_at: dt.datetime
    title: str
    item_count: int
    item_type: str

    @classmethod
    def from_json(cls, data: ResponseT) -> Group:
        return cls(
            data["kind"],
            data["etag"],
            data["id"],
            du_parse(data["snippet"]["publishedAt"]),
            data["snippet"]["title"],
            int(data["contentDetails"]["itemCount"]),
            data["contentDetails"]["itemType"],
        )

    @property
    def data(self) -> ResponseT:
        return {
            "kind": self.kind,
            "etag": self.etag,
            "id": self.id,
            "snippet": {
                "publishedAt": (
                    self.published_at.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                ),
                "title": self.title,
            },
            "contentDetails": {
                "itemCount": str(self.item_count),
                "itemType": self.item_type,
            },
        }


@dataclass(frozen=True)
class GroupList(_Resource):
    __slots__ = ("items", "next_page_token")

    items: list[Group]
    next_page_token: str

    def __getitem__(self, key: int) -> Group:
        return self.items[key]

    @classmethod
    def from_json(cls, data: ResponseT) -> GroupList:
        return cls(
            data["kind"],
            data.get("etag") or None,
            [Group.from_json(item) for item in data["items"]],
            data["nextPageToken"],
        )

    @property
    def data(self) -> ResponseT:
        return {
            "kind": self.kind,
            "etag": self.etag,
            "items": [group.data for group in self.items],
            "nextPageToken": self.next_page_token,
        }


@dataclass(frozen=True)
class _GroupItemResource:
    __slots__ = ("kind", "id")

    kind: str
    id: str


@dataclass(frozen=True)
class GroupItem(_Resource):
    __slots__ = ("id", "group_id", "resource")

    id: str
    group_id: str
    resource: _GroupItemResource

    @classmethod
    def from_json(cls, data: ResponseT) -> GroupItem:
        return cls(
            data["kind"],
            data["etag"],
            data["id"],
            data["groupId"],
            _GroupItemResource(
                data["resource"]["kind"],
                data["resource"]["id"],
            ),
        )

    @property
    def data(self) -> ResponseT:
        return {
            "kind": self.kind,
            "etag": self.etag,
            "id": self.id,
            "groupId": self.group_id,
            "resource": {
                "kind": self.resource.kind,
                "id": self.resource.id,
            },
        }


@dataclass(frozen=True)
class GroupItemList(_Resource):
    __slots__ = "items"

    items: list[GroupItem]

    def __getitem__(self, key: int) -> GroupItem:
        return self.items[key]

    @classmethod
    def from_json(cls, data: ResponseT) -> GroupItemList:
        return cls(
            data["kind"],
            data["etag"],
            [GroupItem.from_json(item) for item in data["items"]],
        )

    @property
    def data(self) -> ResponseT:
        return {
            "kind": self.kind,
            "etag": self.etag,
            "items": [g_item.data for g_item in self.items],
        }
