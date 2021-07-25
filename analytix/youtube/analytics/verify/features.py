__all__ = (
    "Dimensions",
    "Filters",
    "Metrics",
    "SortOptions",
    "Required",
    "ExactlyOne",
    "OneOrMore",
    "Optional",
    "ZeroOrOne",
    "ZeroOrMore",
)

import abc

from analytix.errors import InvalidRequest

from .constants import *


class FeatureType(metaclass=abc.ABCMeta):
    __slots__ = ("sets",)

    def __init__(self, *sets):
        self.sets = sets
        self.every = []
        for s in sets:
            self.every.extend(s.values)

    def __iter__(self):
        return iter(self.every)

    def verify(self, against):
        raise NotImplementedError(
            "you should not attempt to verify this ABC directly"
        )


class FeatureSet(metaclass=abc.ABCMeta):
    __slots__ = ("values",)

    def __init__(self, *values):
        self.values = set(values)

    def __iter__(self):
        return iter(self.values)

    def verify(self, against, ftype):
        raise NotImplementedError(
            "you should not attempt to verify this ABC directly"
        )


class Dimensions(FeatureType):
    def verify(self, against):
        against = set(against)

        diff = against - set(YOUTUBE_ANALYTICS_ALL_DIMENSIONS)
        if diff:
            raise InvalidRequest(
                "one or more dimensions you provided are invalid "
                f"({', '.join(diff)})"
            )

        diff = against - set(self.every)
        if diff:
            raise InvalidRequest(
                "one or more dimensions you provided are not supported by the "
                f"selected report type ({', '.join(diff)})"
            )

        for s in self.sets:
            s.verify(against, "dimension")


class Filters(FeatureType):
    def __init__(self, *sets):
        self.sets = sets
        self.every = []
        for s in sets:
            self.every.extend([v.split("==")[0] for v in s.values])

    def verify(self, against):
        keys = set(against.keys())

        diff = keys - set(YOUTUBE_ANALYTICS_ALL_FILTERS)
        if diff:
            raise InvalidRequest(
                "one or more filters you provided are invalid "
                f"({', '.join(diff)})"
            )

        diff = keys - set(self.every)
        if diff:
            raise InvalidRequest(
                "one or more filters you provided are not supported by the "
                f"selected report type ({', '.join(diff)})"
            )

        for s in self.sets:
            s.verify(against, "filter")

        for k, v in against.items():
            valid_values = YOUTUBE_ANALYTICS_VALID_FILTER_OPTIONS[k]
            if against[k] and valid_values and v not in valid_values:
                raise InvalidRequest(
                    f"'{v}' is not a valid value for filter '{k}'"
                )


class Metrics:
    def __init__(self, *values):
        self.values = values

    def __iter__(self):
        return iter(self.values)

    def verify(self, against):
        against = set(against)

        diff = against - set(YOUTUBE_ANALYTICS_ALL_METRICS)
        if diff:
            raise InvalidRequest(
                "one or more metrics you provided are invalid "
                f"({', '.join(diff)})"
            )

        diff = against - set(self.values)
        if diff:
            raise InvalidRequest(
                "one or more metrics you provided are not supported by the "
                f"selected report type ({', '.join(diff)})"
            )


class SortOptions:
    def __init__(self, *values):
        self.values = values

    def __iter__(self):
        return iter(self.values)

    def verify(self, against):
        against = set([a.strip("-") for a in against])

        diff = against - set(YOUTUBE_ANALYTICS_ALL_METRICS)
        if diff:
            raise InvalidRequest(
                "one or more sort options you provided are invalid "
                f"({', '.join(diff)})"
            )

        diff = against - set(self.values)
        if diff:
            raise InvalidRequest(
                "one or more sort options you provided are not supported by "
                f"the selected report type ({', '.join(diff)})"
            )


class Required(FeatureSet):
    def verify(self, against, ftype):
        values = []
        for v in self.values:
            k = v.split("==")
            if len(k) == 2:
                if k[0] in against and (k[1] != against[k[0]]):
                    raise InvalidRequest(
                        f"filter '{k[0]}' must be set to '{k[1]}' for the "
                        "selected report type"
                    )
            values.append(k[0])

        if len(set(values) & set(against)) != len(self.values):
            raise InvalidRequest(
                f"expected all {ftype}s from '{', '.join(values)}', "
                f"got {len(against)}"
            )


class ExactlyOne(FeatureSet):
    def verify(self, against, ftype):
        if len(self.values & set(against)) != 1:
            raise InvalidRequest(
                f"expected 1 {ftype} from '{', '.join(self.values)}', "
                f"got {len(against)}"
            )


class OneOrMore(FeatureSet):
    def verify(self, against, ftype):
        if len(self.values & set(against)) == 0:
            raise InvalidRequest(
                f"expected at least 1 {ftype} from "
                f"'{', '.join(self.values)}', got 0"
            )


class Optional(FeatureSet):
    def verify(self, against, ftype):
        # This doesn't need any verification.
        pass


class ZeroOrOne(FeatureSet):
    def verify(self, against, ftype):
        if len(self.values & set(against)) > 1:
            raise InvalidRequest(
                f"expected 0 or 1 {ftype}s from '{', '.join(self.values)}', "
                f"got {len(against)}"
            )


class ZeroOrMore(FeatureSet):
    def verify(self, against, ftype):
        # This doesn't need any verification.
        pass
