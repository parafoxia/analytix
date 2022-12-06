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

import logging
import sys
import warnings

import pytest

from analytix import utils
from analytix.errors import MissingOptionalComponents

if sys.version_info >= (3, 8):
    from unittest import mock
else:
    import mock


def test_can_use_installed():
    assert utils.can_use("analytix")


def test_can_use_not_installed():
    assert not utils.can_use("rickroll")


def test_can_use_required_installed():
    assert utils.can_use("analytix", required=True)


def test_can_use_required_not_installed():
    with pytest.raises(
        MissingOptionalComponents,
        match=r"some necessary libraries are not installed \(hint: pip install rickroll\)",
    ):
        utils.can_use("rickroll", required=True)

    with pytest.raises(
        MissingOptionalComponents,
        match=r"some necessary libraries are not installed \(hint: pip install rickroll barney\)",
    ):
        utils.can_use("rickroll", "barney", required=True)


def test_requires_installed():
    @utils.requires("analytix")
    def test():
        return True

    assert test()


def test_requires_not_installed():
    @utils.requires("rickroll")
    def test():
        return True

    with pytest.raises(
        MissingOptionalComponents,
        match=r"some necessary libraries are not installed \(hint: pip install rickroll\)",
    ):
        test()


def test_warn_with_logger(caplog):
    utils.warn("Rickroll warning!")
    assert "Rickroll warning!" in caplog.text


@mock.patch.object(logging.Logger, "hasHandlers", return_value=False)
def test_warn_without_logger(_):
    with warnings.catch_warnings(record=True) as w:
        utils.warn("Sandstorm warning!")
        assert len(w) == 1
        assert issubclass(w[-1].category, Warning)
        assert "Sandstorm warning!" in str(w[-1].message)


def test_warn_on_call_with_logger(caplog):
    @utils.warn_on_call("Rickroll warning!")
    def test():
        return True

    test()
    assert "Rickroll warning!" in caplog.text


@mock.patch.object(logging.Logger, "hasHandlers", return_value=False)
def test_warn_on_call_without_logger(_):
    @utils.warn_on_call("Sandstorm warning!")
    def test():
        return True

    with warnings.catch_warnings(record=True) as w:
        test()
        assert len(w) == 1
        assert issubclass(w[-1].category, Warning)
        assert "Sandstorm warning!" in str(w[-1].message)
