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
import time
from functools import partial
from multiprocessing.pool import ThreadPool
from urllib.request import urlopen

import pytest

from analytix.auth.flow import run_flow
from analytix.errors import AuthorisationError


def test_run_flow(auth_params, caplog):
    auth_params["redirect_uri"] = f"http://localhost:8081"

    def req():
        # Sleeping for a tick makes sure the server is set up before a
        # request is made to it.
        time.sleep(0.1)
        url = f"http://localhost:8081?state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927&code=a1b2c3d4e5"
        urlopen(url)

    with caplog.at_level(logging.DEBUG):
        pool = ThreadPool(processes=2)
        res = pool.map(lambda f: f(), [partial(run_flow, auth_params), req])
        pool.close()
        pool.join()

        assert res[0] == "a1b2c3d4e5"
        assert "Received request (200)" in caplog.text


def test_run_flow_invalid_url(auth_params, caplog):
    auth_params["redirect_uri"] = "barney_the_dinosaur"

    def req():
        # Sleeping for a tick makes sure the server is set up before a
        # request is made to it.
        time.sleep(0.1)
        url = "http://localhost:8082?state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927&code=a1b2c3d4e5"
        urlopen(url)

    with caplog.at_level(logging.DEBUG):
        pool = ThreadPool(processes=2)
        with pytest.raises(AuthorisationError, match="invalid redirect URI"):
            pool.map(lambda f: f(), [partial(run_flow, auth_params), req])
        pool.close()
        pool.join()


def test_run_flow_invalid_state(auth_params, caplog):
    auth_params["redirect_uri"] = f"http://localhost:8083"

    def req():
        # Sleeping for a tick makes sure the server is set up before a
        # request is made to it.
        time.sleep(0.1)
        url = "http://localhost:8083?state=rickroll&code=a1b2c3d4e5"
        urlopen(url)

    with caplog.at_level(logging.DEBUG):
        pool = ThreadPool(processes=2)
        with pytest.raises(AuthorisationError, match="invalid state"):
            pool.map(lambda f: f(), [partial(run_flow, auth_params), req])
        pool.close()
        pool.join()
