class AnalytixError(Exception):
    """The base exception class for analytix."""

    pass


class ServiceAlreadyExists(AnalytixError):
    """An attempt to create a service was made while one already exists."""

    pass


class InvalidScopes(AnalytixError):
    """Invalid scopes were provided."""

    pass


class InvalidRequest(AnalytixError):
    """Invalid information was passed to a request."""

    pass


class Deprecated(AnalytixError):
    """A feature of analytix or the YouTube Analytics API is deprecated."""

    pass


class MissingOptionalComponents(AnalytixError):
    """Some optional components are missing."""

    pass


class UtilityError(AnalytixError):
    """Something went wrong inside a util function."""

    pass
