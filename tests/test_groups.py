# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

from unittest import mock

from analytix.auth.tokens import Tokens
from analytix.client import Client
from analytix.groups import Group
from analytix.groups import GroupItem
from analytix.groups import GroupItemList
from analytix.groups import GroupList
from analytix.mixins import RequestMixin


def test_create_group_from_json(client, group_data, group):
    assert Group.from_json(client, group_data) == group


def test_group_data_property(group_data, group):
    assert group.data == group_data


def test_group_data_fetch_items(
    group: Group,
    group_item_list,
    group_item_list_response,
    tokens: Tokens,
):
    with (
        mock.patch.object(
            RequestMixin,
            "_request",
            return_value=group_item_list_response,
        ),
        mock.patch.object(Client, "authorise", return_value=tokens),
    ):
        assert group.fetch_items() == group_item_list


def test_create_group_list_from_json(client, group_list_data, group_list):
    assert GroupList.from_json(client, group_list_data) == group_list


def test_group_list_from_json_no_groups(
    client,
    empty_group_list_data,
    empty_group_list,
):
    assert GroupList.from_json(client, empty_group_list_data) == empty_group_list


def test_group_list_data_property(group_list_data, group_list):
    assert group_list.data == group_list_data


def test_group_list_get_item(group_list, group):
    assert group_list[0] == group_list.items[0] == group


def test_group_list_is_iterable(group_list, group):
    for g in group_list:
        # There's only one item.
        assert g == group


def test_create_group_item_from_json(group_item_data):
    group = GroupItem.from_json(group_item_data)
    assert group.kind == "youtube#groupItem"
    assert group.etag == "f6g7h8i9j0"
    assert group.id == "e5d4c3b2a1"
    assert group.group_id == "a1b2c3d4e5"
    assert group.resource.kind == "youtube#video"
    assert group.resource.id == "j0i9h8g7f6"


def test_group_item_data_property(group_item_data, group_item):
    assert group_item.data == group_item_data


def test_create_group_item_list_from_json(group_item_list_data, group_item_list):
    assert GroupItemList.from_json(group_item_list_data) == group_item_list


def test_group_item_list_data_property(group_item_list_data, group_item_list):
    assert group_item_list.data == group_item_list_data


def test_group_item_list_get_item(group_item_list, group_item):
    assert group_item_list[0] == group_item_list.items[0] == group_item


def test_group_item_list_is_iterable(group_item_list, group_item):
    for i in group_item_list:
        # There's only one item.
        assert i == group_item
