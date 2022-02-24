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

from __future__ import annotations

import json
import logging
import pathlib
import typing as t
from dataclasses import dataclass

import aiofiles

_TT = t.Union[str, int]

log = logging.getLogger(__name__)


@dataclass()
class Tokens:
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str

    def __getitem__(self, key: str) -> _TT:
        return t.cast(_TT, getattr(self, key))

    @classmethod
    def from_data(cls, data: dict[str, str | int]) -> Tokens:
        return cls(**data)  # type: ignore

    @classmethod
    def from_file(cls, path: pathlib.Path | str) -> Tokens:
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        log.debug(f"Loading tokens from {path.resolve()}...")

        with open(path) as f:
            data = json.load(f)

        log.info("Tokens loaded!")
        return cls(**data)

    @classmethod
    async def afrom_file(cls, path: pathlib.Path | str) -> Tokens:
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        log.debug(f"Loading tokens from {path.resolve()}...")

        async with aiofiles.open(path) as f:
            data = json.loads(await f.read())

        log.info("Tokens loaded!")
        return cls(**data)

    def update(self, data: dict[str, str | int]) -> None:
        for k, v in data.items():
            setattr(self, k, v)

        log.info("Tokens updated!")

    def to_dict(self) -> dict[str, str | int]:
        return {
            "access_token": self.access_token,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "token_type": self.token_type,
        }

    def write(self, path: pathlib.Path | str) -> None:
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        with open(path, "w") as f:
            json.dump(self.to_dict(), f)

        log.info(f"Tokens saved to {path.resolve()}")

    async def awrite(self, path: pathlib.Path | str) -> None:
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        async with aiofiles.open(path, "w") as f:
            await f.write(json.dumps(self.to_dict()))

        log.info(f"Tokens saved to {path.resolve()}")
