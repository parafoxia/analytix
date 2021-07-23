class AnalytixError(Exception):
    """The base exception class for analytix."""

    pass


class InvalidScopes(AnalytixError):
    pass


class InvalidRequest(AnalytixError):
    pass


class Deprecated(AnalytixError):
    pass


class MissingOptionalComponents(AnalytixError):
    pass


class HTTPError(AnalytixError):
    pass
