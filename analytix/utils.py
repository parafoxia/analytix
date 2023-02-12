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

__all__ = ("can_use", "requires", "process_path")

import logging
import typing as t
from functools import wraps
from pathlib import Path

from pkg_resources import working_set

from analytix.errors import MissingOptionalComponents

if t.TYPE_CHECKING:
    from analytix.types import PathLikeT

    _FuncT = t.Callable[..., t.Any]

_log = logging.getLogger(__name__)


def can_use(*packages: str, required: bool = False) -> bool:
    ws = [p.key for p in working_set]
    can_use = all(p in ws for p in packages)

    if required and not can_use:
        raise MissingOptionalComponents(*packages)

    return can_use


def requires(*packages: str) -> t.Callable[[_FuncT], _FuncT]:
    def decorator(func: _FuncT) -> _FuncT:
        @wraps(func)
        def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
            can_use(*packages, required=True)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def process_path(path: PathLikeT, extension: str, overwrite: bool) -> Path:
    if not isinstance(path, Path):
        path = Path(path)

    if path.suffix != extension:
        path = Path(path.name + extension)

    if not overwrite and path.is_file():
        raise FileExistsError("file already exists and `overwrite` is set to False")

    return path
