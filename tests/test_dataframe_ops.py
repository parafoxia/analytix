# Copyright (c) 2021, Ethan Henderson
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
import sys

import pytest

from analytix import YouTubeAnalytics


@pytest.fixture()
def client():
    client = YouTubeAnalytics.from_file("./secrets/secrets.json")
    client.authorise()
    return client


@pytest.mark.skipif(
    sys.version_info >= (3, 11, 0),
    reason="pandas does not support Python 3.11",
)
def test_day_is_datetime(client):
    import pandas as pd

    report = client.retrieve(dt.date(2021, 1, 1), dimensions=("day",))
    df = report.to_dataframe()
    assert pd.api.types.is_datetime64_ns_dtype(df["day"])


@pytest.mark.skipif(
    sys.version_info >= (3, 11, 0),
    reason="pandas does not support Python 3.11",
)
def test_month_is_datetime(client):
    import pandas as pd

    report = client.retrieve(
        dt.date(2021, 1, 1), dt.date(2021, 6, 1), dimensions=("month",)
    )
    df = report.to_dataframe()
    assert pd.api.types.is_datetime64_ns_dtype(df["month"])


@pytest.mark.skipif(
    sys.version_info >= (3, 11, 0),
    reason="pandas does not support Python 3.11",
)
def test_metrics_are_numeric(client):
    import pandas as pd

    report = client.retrieve(dt.date(2021, 1, 1), dimensions=("day",))
    df = report.to_dataframe()
    for series in df.iloc[:, 1:]:
        assert pd.api.types.is_numeric_dtype(df[series])
