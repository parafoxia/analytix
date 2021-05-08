from analytix.errors import InvalidRequest

from . import abc, valid


class Dimensions(abc.FeatureType):
    def verify(self, against):
        against = set(against)

        diff = against - set(valid.ALL_DIMENSIONS)
        if diff:
            raise InvalidRequest(
                f"one or more dimensions you provided are invalid ({', '.join(diff)})"
            )

        diff = against - set(self.every)
        if diff:
            raise InvalidRequest(
                "one or more dimensions you provided are not supported by the "
                f"current report type ({', '.join(diff)})"
            )

        for s in self.sets:
            s.verify(against, "dimension")


class Filters(abc.FeatureType):
    def __init__(self, *sets):
        self.sets = sets
        self.every = []
        for s in sets:
            self.every.extend([v.split("==")[0] for v in s.values])

    def verify(self, against):
        keys = set(against.keys())

        diff = keys - set(valid.ALL_FILTERS)
        if diff:
            raise InvalidRequest(
                f"one or more filters you provided are invalid ({', '.join(diff)})"
            )

        diff = keys - set(self.every)
        if diff:
            raise InvalidRequest(
                "one or more filters you provided are not supported by the "
                f"report type you are trying to use ({', '.join(diff)})"
            )

        for s in self.sets:
            s.verify(against, "filter")

        for k, v in against.items():
            if against[k] and v not in valid.VALID_FILTER_OPTIONS[k]:
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

        diff = against - set(valid.ALL_METRICS)
        if diff:
            raise InvalidRequest(
                f"one or more metrics you provided are invalid ({', '.join(diff)})"
            )

        diff = against - set(self.values)
        if diff:
            raise InvalidRequest(
                "one or more metrics you provided are not supported by the "
                f"selected report type ({', '.join(diff)})"
            )


class Required(abc.FeatureSet):
    def verify(self, against, ftype):
        values = []
        for v in self.values:
            k = v.split("==")
            if len(k) == 2:
                if k[1] != against[k[0]]:
                    raise InvalidRequest(
                        f"filter '{k[0]}' must be set to '{k[1]}' for the selected report type"
                    )
            values.append(k[0])

        if len(set(values) & set(against)) != len(self.values):
            raise InvalidRequest(
                f"expected all {ftype}s from '{', '.join(values)}', got {len(against)}"
            )


class ExactlyOne(abc.FeatureSet):
    def verify(self, against, ftype):
        if len(self.values & set(against)) != 1:
            raise InvalidRequest(
                f"expected 1 {ftype} from '{', '.join(self.values)}', got {len(against)}"
            )


class OneOrMore(abc.FeatureSet):
    def verify(self, against, ftype):
        if len(self.values & set(against)) == 0:
            raise InvalidRequest(
                f"expected at least 1 {ftype} from '{', '.join(self.values)}', got 0"
            )


class Optional(abc.FeatureSet):
    def verify(self, against, ftype):
        # This doesn't need any verification.
        pass


class ZeroOrOne(abc.FeatureSet):
    def verify(self, against, ftype):
        if len(self.values & set(against)) > 1:
            raise InvalidRequest(
                f"expected 0 or 1 {ftype}s from '{', '.join(self.values)}', got {len(against)}"
            )


class ZeroOrMore(abc.FeatureSet):
    def verify(self, against, ftype):
        # This doesn't need any verification.
        pass
