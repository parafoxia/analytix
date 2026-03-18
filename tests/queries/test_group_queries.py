# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

from analytix.queries import API_GROUP_ITEMS_URL
from analytix.queries import API_GROUPS_URL
from analytix.queries import GroupItemQuery
from analytix.queries import GroupQuery


def test_group_create_defaults():
    query = GroupQuery()
    assert query.ids == ()
    assert query.next_page_token is None


def test_group_create_custom():
    query = GroupQuery(ids=("a1b2c3d4e5", "f6g7h8i9j0"), next_page_token="rickroll")
    assert query.ids == ("a1b2c3d4e5", "f6g7h8i9j0")
    assert query.next_page_token == "rickroll"


def test_group_url_property():
    query = GroupQuery(ids=("a1b2c3d4e5", "f6g7h8i9j0"), next_page_token="rickroll")
    assert (
        query.url
        == f"{API_GROUPS_URL}?id=a1b2c3d4e5,f6g7h8i9j0&next_page_token=rickroll"
    )


def test_group_url_property_no_next_page_token():
    query = GroupQuery(ids=("a1b2c3d4e5", "f6g7h8i9j0"))
    assert query.url == f"{API_GROUPS_URL}?id=a1b2c3d4e5,f6g7h8i9j0"


def test_group_item_create_custom():
    query = GroupItemQuery("a1b2c3d4e5")
    assert query.group_id == "a1b2c3d4e5"


def test_group_item_url_property():
    query = GroupItemQuery("a1b2c3d4e5")
    assert query.url == f"{API_GROUP_ITEMS_URL}?groupId=a1b2c3d4e5"
