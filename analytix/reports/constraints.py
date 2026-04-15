# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import abc
from collections.abc import Collection
from enum import Enum

from analytix.errors import ConstraintError
from analytix.errors import ValidationError


class ConstraintTarget(Enum):
    DIMENSIONS = "dimension"
    FILTERS = "filter"
    METRICS = "metric"
    SORT_OPTIONS = "sort option"


class Constraint(abc.ABC):
    def __init__(self, *fields: Collection[str]) -> None:
        self.fields = set(fields)

    @property
    def keys(self) -> set[str]:
        return {field.split("==")[0] for field in self.fields}

    @abc.abstractmethod
    def validate(
        self,
        inputs: set[str],
        target: ConstraintTarget,
    ) -> list[ValidationError]:
        raise NotImplementedError


class Required(Constraint):
    def validate(
        self,
        inputs: set[str],
        target: ConstraintTarget,
    ) -> list[ValidationError]:
        if missing := self.keys - inputs:
            err = ConstraintError.format(
                "expected all {target}s from {keys}, got {count}",
                target=target.value,
                keys=self.keys,
                count=len(inputs),
            )
            err.add_note(f"Missing: {missing}")
            return [err]
        return []


class ExactlyOne(Constraint):
    def validate(
        self,
        inputs: set[str],
        target: ConstraintTarget,
    ) -> list[ValidationError]:
        if len(self.keys & inputs) != 1:
            err = ConstraintError.format(
                "expected 1 {target} from {keys}, got {count}",
                target=target.value,
                keys=self.keys,
                count=len(inputs),
            )
            err.add_note(f"You provided: {inputs}")
            return [err]
        return []


class OneOrMore(Constraint):
    def validate(
        self,
        inputs: set[str],
        target: ConstraintTarget,
    ) -> list[ValidationError]:
        if not (self.keys & inputs):
            err = ConstraintError.format(
                "expected at least 1 {target} from {keys}, got {count}",
                target=target.value,
                keys=self.keys,
                count=len(inputs),
            )
            err.add_note(f"You provided: {inputs}")
            return [err]
        return []


class Optional(Constraint):
    def validate(
        self,
        inputs: set[str],
        target: ConstraintTarget,
    ) -> list[ValidationError]:
        # No validation required.
        return []


class ZeroOrOne(Constraint):
    def validate(
        self,
        inputs: set[str],
        target: ConstraintTarget,
    ) -> list[ValidationError]:
        if len(self.keys & inputs) > 1:
            err = ConstraintError.format(
                "expected 0 or 1 {target}s from {keys}, got {count}",
                target=target.value,
                keys=self.keys,
                count=len(inputs),
            )
            err.add_note(f"You provided: {inputs}")
            return [err]
        return []


ZeroOrMore = Optional
