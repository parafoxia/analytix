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

import abc
import typing as t


class ReportType(metaclass=abc.ABCMeta):
    ...


class DetailedReportType(ReportType, metaclass=abc.ABCMeta):
    ...


class FeatureType(metaclass=abc.ABCMeta):
    __slots__ = ("values",)

    def __init__(self, *args: SetType) -> None:
        self.values = set(args)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(values={self.values})"

    @abc.abstractmethod
    def validate(self, inputs: t.Iterable[str]) -> None:
        raise NotImplementedError


class SegmentedFeatureType(FeatureType, metaclass=abc.ABCMeta):
    __slots__ = ("values",)

    @property
    def every(self) -> set[str]:
        every = set()

        for set_type in self.values:
            every |= set_type.values

        return every

    @abc.abstractmethod
    def validate(self, inputs: t.Iterable[str]) -> None:
        raise NotImplementedError


class SetType(metaclass=abc.ABCMeta):
    __slots__ = ("values", "expd_keys")

    def __init__(self, *args: str) -> None:
        self.values = set(args)
        self.expd_keys = {v[: v.index("=")] if "==" in v else v for v in self.values}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(values={self.values})"

    @abc.abstractmethod
    def validate_dimensions(self, inputs: set[str]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def validate_filters(self, keys: set[str], expd_keys: set[str]) -> None:
        raise NotImplementedError
