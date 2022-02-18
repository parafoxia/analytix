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

import typing as t

from analytix import data, errors
from analytix.abc import FeatureType, SegmentedFeatureType, SetType


class Metrics(FeatureType):
    def validate(self, inputs: t.Iterable[str]) -> None:
        if not len(inputs):
            raise errors.MissingMetrics()

        if not isinstance(inputs, set):
            inputs = set(inputs)

        diff = inputs - set(data.ALL_METRICS)
        if diff:
            raise errors.InvalidMetrics(diff)

        diff = inputs - self.values
        if diff:
            raise errors.UnsupportedMetrics(diff)


class SortOptions(FeatureType):
    def validate(self, inputs: t.Iterable[str]) -> None:
        inputs = set(i.strip("-") for i in inputs)

        diff = inputs - set(data.ALL_METRICS)
        if diff:
            raise errors.InvalidSortOptions(diff)

        diff = inputs - self.values
        if diff:
            raise errors.UnsupportedSortOptions(diff)


class Dimensions(SegmentedFeatureType):
    def validate(self, inputs: t.Iterable[str]) -> None:
        if not isinstance(inputs, set):
            inputs = set(inputs)

        diff = inputs - set(data.ALL_DIMENSIONS)
        if diff:
            raise errors.InvalidDimensions(diff)

        diff = inputs - self.every
        if diff:
            raise errors.UnsupportedDimensions(diff)

        for set_type in self.values:
            set_type.validate_dimensions(inputs)


class Filters(SegmentedFeatureType):
    @property
    def every_key(self) -> set[str]:
        return {v[: v.index("=")] if "==" in v else v for v in self.every}

    @property
    def locked(self) -> dict[str, str]:
        locked = {}

        for set_type in self.values:
            for value in filter(lambda v: "==" in v, set_type.values):
                k, v = value.split("==")
                locked.update({k: v})

        return locked

    def validate(self, inputs: dict[str, str]) -> None:
        keys = set(inputs.keys())
        locked = self.locked

        diff = keys - set(data.ALL_FILTERS)
        if diff:
            raise errors.InvalidFilters(diff)

        for k, v in inputs.items():
            valid = data.VALID_FILTER_OPTIONS[k]

            if valid and (v not in valid):
                raise errors.InvalidFilterValue(k, v)

            if k in locked.keys():
                if v != locked[k]:
                    raise errors.UnsupportedFilterValue(k, v)

        diff = keys - self.every_key
        if diff:
            raise errors.UnsupportedFilters(diff)

        for set_type in self.values:
            set_type.validate_filters(keys)


class Required(SetType):
    def validate_dimensions(self, inputs: set[str]) -> None:
        if self.values & inputs == self.values:
            return

        common = len(inputs & self.values)
        raise errors.InvalidSetOfDimensions("all", common, self.values)

    def validate_filters(self, keys: set[str]) -> None:
        if self.expd_keys & keys == self.expd_keys:
            return

        common = len(keys & self.expd_keys)
        raise errors.InvalidSetOfFilters("all", common, self.values)


class ExactlyOne(SetType):
    def validate_dimensions(self, inputs: set[str]) -> None:
        if len(self.values & inputs) == 1:
            return

        common = len(inputs & self.values)
        raise errors.InvalidSetOfDimensions("1", common, self.values)

    def validate_filters(self, keys: set[str]) -> None:
        if len(self.expd_keys & keys) == 1:
            return

        common = len(keys & self.expd_keys)
        raise errors.InvalidSetOfFilters("1", common, self.values)


class OneOrMore(SetType):
    def validate_dimensions(self, inputs: set[str]) -> None:
        if len(self.values & inputs) > 0:
            return

        common = len(inputs & self.values)
        raise errors.InvalidSetOfDimensions("at least 1", common, self.values)

    def validate_filters(self, keys: set[str]) -> None:
        if len(self.expd_keys & keys) > 0:
            return

        common = len(keys & self.expd_keys)
        raise errors.InvalidSetOfFilters("at least 1", common, self.values)


class Optional(SetType):
    def validate_dimensions(self, inputs: set[str]) -> None:
        # No verifiction required.
        ...

    def validate_filters(self, keys: set[str]) -> None:
        # No verifiction required.
        ...


class ZeroOrOne(SetType):
    def validate_dimensions(self, inputs: set[str]) -> None:
        if len(self.values & inputs) < 2:
            return

        common = len(inputs & self.values)
        raise errors.InvalidSetOfDimensions("0 or 1", common, self.values)

    def validate_filters(self, keys: set[str]) -> None:
        if len(self.expd_keys & keys) < 2:
            return

        common = len(keys & self.expd_keys)
        raise errors.InvalidSetOfFilters("0 or 1", common, self.values)


class ZeroOrMore(SetType):
    def validate_dimensions(self, inputs: set[str]) -> None:
        # No verifiction required.
        ...

    def validate_filters(self, keys: set[str]) -> None:
        # No verifiction required.
        ...
