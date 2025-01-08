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

"""Group interfaces for analytix.

You should never need to create any of these yourself.
"""

__all__ = ("Group", "GroupItem", "GroupItemList", "GroupList")

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional

if TYPE_CHECKING:
    from analytix.shard import Shard


@dataclass(frozen=True)
class _Resource:
    __slots__ = ("etag", "kind")

    kind: str
    etag: Optional[str]


@dataclass(frozen=True)
class Group(_Resource):
    """A group.

    Parameters
    ----------
    kind
        The kind of resource this is. This will always be
        "youtube#group".
    etag
        The Etag of this resource.
    id
        The ID that YouTube uses to uniquely identify the group.
    published_at
        The date and time that the group was created.
    title
        The group name.
    item_count
        The number of items in the group.
    item_type
        The type of resources that the group contains.
    shard
        The shard instance used to fetch this group.
    """

    __slots__ = ("id", "item_count", "item_type", "published_at", "shard", "title")

    id: str
    published_at: dt.datetime
    title: str
    item_count: int
    item_type: str
    shard: "Shard"

    @classmethod
    def from_json(cls, shard: "Shard", data: Dict[str, Any]) -> "Group":
        """Create a new `Group` instance from JSON data.

        ???+ note "Changed in version 5.0"
            This now takes the shard instance used to fetch the data.

        Parameters
        ----------
        shard
            The shard instance used to fetch the data.
        data
            The raw JSON data from the API.

        Returns
        -------
        Group
            The newly created instance.
        """
        return cls(
            data["kind"],
            data["etag"],
            data["id"],
            dt.datetime.fromisoformat(
                data["snippet"]["publishedAt"].replace("Z", "+00:00"),
            ),
            data["snippet"]["title"],
            int(data["contentDetails"]["itemCount"]),
            data["contentDetails"]["itemType"],
            shard,
        )

    @property
    def data(self) -> Dict[str, Any]:
        """The raw data for this group in JSON format.

        Returns
        -------
        Dict[str, Any]
            The response data.
        """
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

    def fetch_items(self) -> "GroupItemList":
        """Fetch a list of all items within this group.

        !!! note "New in version 5.0"

        Returns
        -------
        GroupItemList
            An object containing the list of group items and the next
            page token.

        Raises
        ------
        BadRequest
            Your request was invalid.
        Unauthorised
            Your access token is invalid.
        Forbidden
            You tried to access data you're not allowed to access. If
            your channel is not partnered, this is raised when you try
            to access monetary data.
        """
        return self.shard.fetch_group_items(self.id)


@dataclass(frozen=True)
class GroupList(_Resource):
    """A list of groups.

    Parameters
    ----------
    kind
        The kind of resource this is. This will always be
        "youtube#groupListResponse".
    etag
        The Etag of this resource.
    items
        A list of groups that match the API request parameters. Each
        item in the list represents a group resource.
    next_page_token
        The token that can be used as the value of the `pageToken`
        parameter to retrieve the next page in the result set.
    """

    __slots__ = ("items", "next_page_token")

    items: List["Group"]
    next_page_token: Optional[str]

    def __getitem__(self, key: int) -> "Group":
        return self.items[key]

    def __iter__(self) -> Iterator["Group"]:
        return iter(self.items)

    @classmethod
    def from_json(cls, shard: "Shard", data: Dict[str, Any]) -> "GroupList":
        """Create a new `GroupList` instance from JSON data.

        ???+ note "Changed in version 5.0"
            * This now takes the shard instance used to fetch the data
            * This will no longer raise an error if a channel has no
              groups

        Parameters
        ----------
        shard
            The shard instance used to fetch the data.
        data
            The raw JSON data from the API.

        Returns
        -------
        GroupList
            The newly created instance.
        """
        return cls(
            data["kind"],
            data.get("etag"),
            [Group.from_json(shard, item) for item in data["items"]],
            data.get("nextPageToken"),
        )

    @property
    def data(self) -> Dict[str, Any]:
        """The raw data for this group in JSON format.

        Returns
        -------
        Dict[str, Any]
            The response data.
        """
        return {
            "kind": self.kind,
            "etag": self.etag,
            "items": [group.data for group in self.items],
            "nextPageToken": self.next_page_token,
        }


@dataclass(frozen=True)
class GroupItemResource:
    """A group item resource.

    Parameters
    ----------
    kind
        Identifies the type of resource being added to the group.
    id
        The channel, video, playlist, or asset ID that YouTube uses to
        uniquely identify the item that is being added to the group.
    """

    __slots__ = ("id", "kind")

    kind: str
    id: str


@dataclass(frozen=True)
class GroupItem(_Resource):
    """A group item.

    Parameters
    ----------
    kind
        The kind of resource this is. This will always be
        "youtube#groupItem".
    etag
        The Etag of this resource.
    id
        The ID that YouTube uses to uniquely identify the channel,
        video, playlist, or asset resource that is included in the
        group.
    resource
        The resource object contains information that identifies the
        item being added to the group.

    Notes
    -----
    The `id` parameter does NOT refer to the actual ID of the channel,
    video, playlist, or asset, but instead an ID related to its
    inclusion within the group.

    To get the actual ID of the resource, use `resource.id`.
    """

    __slots__ = ("group_id", "id", "resource")

    id: str
    group_id: str
    resource: "GroupItemResource"

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "GroupItem":
        """Create a new `GroupItem` instance from JSON data.

        Parameters
        ----------
        data
            The raw JSON data from the API.

        Returns
        -------
        GroupItem
            The newly created instance.
        """
        return cls(
            data["kind"],
            data["etag"],
            data["id"],
            data["groupId"],
            GroupItemResource(
                data["resource"]["kind"],
                data["resource"]["id"],
            ),
        )

    @property
    def data(self) -> Dict[str, Any]:
        """The raw data for this group in JSON format.

        Returns
        -------
        Dict[str, Any]
            The response data.
        """
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
    """A list of group items.

    Parameters
    ----------
    kind
        The kind of resource this is. This will always be
        "youtube#groupListResponse".
    etag
        The Etag of this resource.
    items
        A list of items that the group contains. Each item in the list
        represents a groupItem resource.
    """

    __slots__ = "items"

    items: List["GroupItem"]

    def __getitem__(self, key: int) -> "GroupItem":
        return self.items[key]

    def __iter__(self) -> Iterator["GroupItem"]:
        return iter(self.items)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "GroupItemList":
        """Create a new `GroupItemList` instance from JSON data.

        Parameters
        ----------
        data
            The raw JSON data from the API.

        Returns
        -------
        GroupItemList
            The newly created instance.
        """
        return cls(
            data["kind"],
            data["etag"],
            [GroupItem.from_json(item) for item in data["items"]],
        )

    @property
    def data(self) -> Dict[str, Any]:
        """The raw data for this group in JSON format.

        Returns
        -------
        Dict[str, Any]
            The response data.
        """
        return {
            "kind": self.kind,
            "etag": self.etag,
            "items": [g_item.data for g_item in self.items],
        }
