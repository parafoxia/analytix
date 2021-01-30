class AnalytixError(Exception):
    """The base exception class for analytix."""

    pass


class NoAuthorisedService(AnalytixError):
    """Exception thrown when an operatoion that requires authorisation is attempted while no service is no authorised."""

    pass


class ServiceAlreadyExists(AnalytixError):
    """Exception thrown when an attempt to create a service is made while one already exists."""

    pass


class IncompleteRequest(AnalytixError):
    """Exception throws when not enough information has been passed to a request."""

    pass


class InvalidRequest(AnalytixError):
    """Exception throws when invalid information has been passed to a request."""

    pass
