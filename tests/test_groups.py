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

from unittest import mock

from analytix.groups import Group, GroupItem, GroupItemList, GroupList
from analytix.mixins import RequestMixin


def test_create_group_from_json(shard, group_data, group):
    assert Group.from_json(shard, group_data) == group


def test_group_data_property(group_data, group):
    assert group.data == group_data


def test_group_data_fetch_items(
    group: Group, group_item_list, group_item_list_response
):
    with mock.patch.object(
        RequestMixin, "_request", return_value=group_item_list_response
    ):
        assert group.fetch_items() == group_item_list


def test_create_group_list_from_json(shard, group_list_data, group_list):
    assert GroupList.from_json(shard, group_list_data) == group_list


def test_group_list_from_json_no_groups(shard, empty_group_list_data, empty_group_list):
    assert GroupList.from_json(shard, empty_group_list_data) == empty_group_list


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
