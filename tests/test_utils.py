# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import sys
from pathlib import Path

import pytest

from analytix import utils

if sys.version_info >= (3, 8):
    from unittest import mock
else:
    from unittest import mock


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
        "report.json",
    )


@mock.patch.object(Path, "is_file", return_value=False)
def test_process_path_pathlib(_):
    assert utils.process_path(Path("report"), ".json", overwrite=False) == Path(
        "report.json",
    )


@mock.patch.object(Path, "is_file", return_value=True)
def test_process_path_file_exists_overwrite(_):
    assert utils.process_path("report", ".json", overwrite=True) == Path("report.json")


@mock.patch.object(Path, "is_file", return_value=True)
def test_process_path_file_exists_dont_overwrite(_):
    with pytest.raises(
        FileExistsError,
        match="file already exists and `overwrite` is set to False",
    ):
        assert utils.process_path("report", ".json", overwrite=False)
