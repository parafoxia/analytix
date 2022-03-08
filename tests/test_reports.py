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

import json
import os
import platform
import sys
from pathlib import Path

import mock
import pytest

import analytix
from analytix import data, errors
from analytix.report_types import TimeBasedActivity
from analytix.reports import Report

DATA_PATH = Path(__file__).parent / "data"
MOCK_DATA_PATH = DATA_PATH / "test_data.json"
MOCK_CSV_PATH = DATA_PATH / "test_data.csv"
JSON_OUTPUT_PATH = DATA_PATH / "output.json"
CSV_OUTPUT_PATH = DATA_PATH / "output.csv"
TSV_OUTPUT_PATH = DATA_PATH / "output.tsv"


@pytest.fixture()
def request_data():
    with open(MOCK_DATA_PATH) as f:
        return json.load(f)


@pytest.fixture()
def report_type():
    return TimeBasedActivity()


def test_init(request_data, report_type):
    report = Report(request_data, report_type)
    assert report.data == request_data
    assert report.type == report_type
    assert report.columns == [
        "day",
        *[m for m in data.ALL_METRICS_ORDERED if m in data.ALL_VIDEO_METRICS],
    ]
    assert report._ncolumns == 36
    assert report._nrows == 31


@pytest.fixture()
def report():
    with open(MOCK_DATA_PATH) as f:
        data = json.load(f)

    return Report(data, TimeBasedActivity())


def test_shape(report):
    assert report.shape == (31, 36)


def test_to_json(report, request_data):
    report.to_json(str(JSON_OUTPUT_PATH))
    assert JSON_OUTPUT_PATH.is_file()

    with open(JSON_OUTPUT_PATH) as f:
        assert json.load(f) == request_data

    os.remove(JSON_OUTPUT_PATH)


async def test_to_json_async(report, request_data):
    await report.ato_json(str(JSON_OUTPUT_PATH))
    assert JSON_OUTPUT_PATH.is_file()

    with open(JSON_OUTPUT_PATH) as f:
        assert json.load(f) == request_data

    os.remove(JSON_OUTPUT_PATH)


def test_to_json_no_extension(report, request_data):
    report.to_json(str(JSON_OUTPUT_PATH)[:-5])
    assert JSON_OUTPUT_PATH.is_file()

    with open(JSON_OUTPUT_PATH) as f:
        assert json.load(f) == request_data

    os.remove(JSON_OUTPUT_PATH)


async def test_to_json_async_no_extension(report, request_data):
    await report.ato_json(str(JSON_OUTPUT_PATH)[:-5])
    assert JSON_OUTPUT_PATH.is_file()

    with open(JSON_OUTPUT_PATH) as f:
        assert json.load(f) == request_data

    os.remove(JSON_OUTPUT_PATH)


@pytest.fixture()
def mock_csv_data():
    with open(MOCK_CSV_PATH) as f:
        return f.read()


def test_to_csv(report, mock_csv_data):
    report.to_csv(str(CSV_OUTPUT_PATH))
    assert CSV_OUTPUT_PATH.is_file()

    with open(CSV_OUTPUT_PATH) as f:
        assert f.read() == mock_csv_data

    os.remove(CSV_OUTPUT_PATH)


async def test_to_csv_async(report, mock_csv_data):
    await report.ato_csv(str(CSV_OUTPUT_PATH))
    assert CSV_OUTPUT_PATH.is_file()

    with open(CSV_OUTPUT_PATH) as f:
        assert f.read() == mock_csv_data

    os.remove(CSV_OUTPUT_PATH)


def test_to_csv_no_extension(report, mock_csv_data):
    report.to_csv(str(CSV_OUTPUT_PATH)[:-4])
    assert CSV_OUTPUT_PATH.is_file()

    with open(CSV_OUTPUT_PATH) as f:
        assert f.read() == mock_csv_data

    os.remove(CSV_OUTPUT_PATH)


async def test_to_csv_async_no_extension(report, mock_csv_data):
    await report.ato_csv(str(CSV_OUTPUT_PATH)[:-4])
    assert CSV_OUTPUT_PATH.is_file()

    with open(CSV_OUTPUT_PATH) as f:
        assert f.read() == mock_csv_data

    os.remove(CSV_OUTPUT_PATH)


def test_to_tsv(report, mock_csv_data):
    report.to_csv(str(TSV_OUTPUT_PATH), delimiter="\t")
    assert TSV_OUTPUT_PATH.is_file()

    with open(TSV_OUTPUT_PATH) as f:
        assert f.read() == mock_csv_data.replace(",", "\t")

    os.remove(TSV_OUTPUT_PATH)


async def test_to_tsv_async(report, mock_csv_data):
    await report.ato_csv(str(TSV_OUTPUT_PATH), delimiter="\t")
    assert TSV_OUTPUT_PATH.is_file()

    with open(TSV_OUTPUT_PATH) as f:
        assert f.read() == mock_csv_data.replace(",", "\t")

    os.remove(TSV_OUTPUT_PATH)


def test_to_tsv_no_extension(report, mock_csv_data):
    report.to_csv(str(TSV_OUTPUT_PATH)[:-4], delimiter="\t")
    assert TSV_OUTPUT_PATH.is_file()

    with open(TSV_OUTPUT_PATH) as f:
        assert f.read() == mock_csv_data.replace(",", "\t")

    os.remove(TSV_OUTPUT_PATH)


async def test_to_tsv_async_no_extension(report, mock_csv_data):
    await report.ato_csv(str(TSV_OUTPUT_PATH)[:-4], delimiter="\t")
    assert TSV_OUTPUT_PATH.is_file()

    with open(TSV_OUTPUT_PATH) as f:
        assert f.read() == mock_csv_data.replace(",", "\t")

    os.remove(TSV_OUTPUT_PATH)


@pytest.mark.skipif(
    sys.version_info >= (3, 11, 0) or platform.python_implementation() != "CPython",
    reason="pandas does not support Python 3.11 or PyPy",
)
def test_to_dataframe(report, request_data):
    df = report.to_dataframe()
    assert df.shape == (31, 36)
    assert list(df.columns) == report.columns

    for i, row in df.iterrows():
        # We don't need the date to check -- it just complicated things.
        assert list(row)[1:] == request_data["rows"][i][1:]


@pytest.mark.skipif(
    sys.version_info >= (3, 11, 0) or platform.python_implementation() != "CPython",
    reason="pandas does not support Python 3.11 or PyPy",
)
def test_to_dataframe_no_pandas(report):
    with mock.patch.object(analytix, "can_use") as mock_cu:
        mock_cu.return_value = False

        with pytest.raises(errors.MissingOptionalComponents) as exc:
            report.to_dataframe()
        assert (
            str(exc.value)
            == "some necessary libraries are not installed (hint: pip install pandas)"
        )


@pytest.mark.skipif(
    sys.version_info >= (3, 11, 0) or platform.python_implementation() != "CPython",
    reason="pandas does not support Python 3.11 or PyPy",
)
def test_to_dataframe_no_rows(report):
    report._nrows = 0

    with pytest.raises(errors.DataFrameConversionError) as exc:
        report.to_dataframe()
    assert (
        str(exc.value) == "cannot convert to DataFrame as the returned data has no rows"
    )
