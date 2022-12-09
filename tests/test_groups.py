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

import datetime as dt

import pytest
import pytz

from analytix.groups import Group, GroupItem, GroupItemList, GroupList


@pytest.fixture()
def group_data():
    return {
        "kind": "youtube#group",
        "etag": "f6g7h8i9j0",
        "id": "a1b2c3d4e5",
        "snippet": {
            "publishedAt": "2022-11-30T12:34:56.789Z",
            "title": "Barney the Dinosaur",
        },
        "contentDetails": {
            "itemCount": "69",
            "itemType": "youtube#video",
        },
    }


@pytest.fixture()
def group():
    return Group(
        kind="youtube#group",
        etag="f6g7h8i9j0",
        id="a1b2c3d4e5",
        published_at=dt.datetime(2022, 11, 30, 12, 34, 56, 789000, tzinfo=pytz.utc),
        title="Barney the Dinosaur",
        item_count=69,
        item_type="youtube#video",
    )


def test_create_group_from_json(group_data, group):
    assert Group.from_json(group_data) == group


def test_group_data_property(group_data, group):
    assert group.data == group_data


@pytest.fixture()
def group_list_data(group_data):
    return {
        "kind": "youtube#groupListResponse",
        "etag": "f6g7h8i9j0",
        "items": [group_data],
        "nextPageToken": "a1b2c3d4e5",
    }


@pytest.fixture()
def group_list(group):
    return GroupList(
        kind="youtube#groupListResponse",
        etag="f6g7h8i9j0",
        items=[group],
        next_page_token="a1b2c3d4e5",
    )


def test_create_group_list_from_json(group_list_data, group_list):
    assert GroupList.from_json(group_list_data) == group_list


def test_group_list_data_property(group_list_data, group_list):
    assert group_list.data == group_list_data


def test_group_list_get_item(group_list, group):
    assert group_list[0] == group_list.items[0] == group


@pytest.fixture()
def group_item_data():
    return {
        "kind": "youtube#groupItem",
        "etag": "f6g7h8i9j0",
        "id": "e5d4c3b2a1",
        "groupId": "a1b2c3d4e5",
        "resource": {
            "kind": "youtube#video",
            "id": "j0i9h8g7f6",
        },
    }


@pytest.mark.dependency()
def test_create_group_item_from_json(group_item_data):
    group = GroupItem.from_json(group_item_data)
    assert group.kind == "youtube#groupItem"
    assert group.etag == "f6g7h8i9j0"
    assert group.id == "e5d4c3b2a1"
    assert group.group_id == "a1b2c3d4e5"
    assert group.resource.kind == "youtube#video"
    assert group.resource.id == "j0i9h8g7f6"


@pytest.mark.dependency(depends=["test_create_group_item_from_json"])
@pytest.fixture()
def group_item(group_item_data):
    return GroupItem.from_json(group_item_data)


@pytest.mark.dependency(depends=["test_create_group_item_from_json"])
def test_group_item_data_property(group_item_data, group_item):
    assert group_item.data == group_item_data


@pytest.fixture()
def group_item_list_data(group_item_data):
    return {
        "kind": "youtube#groupItemListResponse",
        "etag": "a1b2c3d4e5",
        "items": [group_item_data],
    }


@pytest.fixture()
def group_item_list(group_item):
    return GroupItemList(
        kind="youtube#groupItemListResponse",
        etag="a1b2c3d4e5",
        items=[group_item],
    )


@pytest.mark.dependency(depends=["test_create_group_item_from_json"])
def test_create_group_item_list_from_json(group_item_list_data, group_item_list):
    assert GroupItemList.from_json(group_item_list_data) == group_item_list


@pytest.mark.dependency(depends=["test_create_group_item_from_json"])
def test_group_item_list_data_property(group_item_list_data, group_item_list):
    assert group_item_list.data == group_item_list_data


@pytest.mark.dependency(depends=["test_create_group_item_from_json"])
def test_group_item_list_get_item(group_item_list, group_item):
    assert group_item_list[0] == group_item_list.items[0] == group_item
