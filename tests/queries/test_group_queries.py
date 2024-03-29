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

from analytix.queries import (
    API_GROUP_ITEMS_URL,
    API_GROUPS_URL,
    GroupItemQuery,
    GroupQuery,
)


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
