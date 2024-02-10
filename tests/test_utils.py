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

import sys
from pathlib import Path

import pytest

from analytix import utils

if sys.version_info >= (3, 8):
    from unittest import mock
else:
    import mock


def test_can_use_installed():
    assert utils.can_use("analytix")


def test_can_use_not_installed():
    assert not utils.can_use("rickroll")


@mock.patch.object(Path, "is_file", return_value=False)
def test_process_path_string_no_extension(_):
    assert utils.process_path("report", ".json", overwrite=False) == Path("report.json")


@mock.patch.object(Path, "is_file", return_value=False)
def test_process_path_string_with_extension(_):
    assert utils.process_path("report.json", ".json", overwrite=False) == Path(
        "report.json"
    )


@mock.patch.object(Path, "is_file", return_value=False)
def test_process_path_pathlib(_):
    assert utils.process_path(Path("report"), ".json", overwrite=False) == Path(
        "report.json"
    )


@mock.patch.object(Path, "is_file", return_value=True)
def test_process_path_file_exists_overwrite(_):
    assert utils.process_path("report", ".json", overwrite=True) == Path("report.json")


@mock.patch.object(Path, "is_file", return_value=True)
def test_process_path_file_exists_dont_overwrite(_):
    with pytest.raises(
        FileExistsError, match="file already exists and `overwrite` is set to False"
    ):
        assert utils.process_path("report", ".json", overwrite=False)
