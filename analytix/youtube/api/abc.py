import abc


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
