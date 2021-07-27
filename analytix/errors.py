class AnalytixError(Exception):
    """The base exception class for analytix."""

    pass


class InvalidScopes(AnalytixError):
    """Thrown when one or more invalid scopes are passed to the
    client."""

    pass


class InvalidRequest(AnalytixError):
    """Thrown when analytix finds something wrong with an API
    request."""

    pass


class HTTPError(InvalidRequest):
    """Thrown when the API returns an error. Inherits from
    :class:`InvalidRequest`."""

    pass


class MissingOptionalComponents(AnalytixError):
    """Thrown when an optional component or library is needed to perform
    an action, but it missing."""

    pass
