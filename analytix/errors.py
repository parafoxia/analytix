class AnalytixError(Exception):
    pass


class NoAuthorisedService(AnalytixError):
    pass


class ServiceAlreadyExists(AnalytixError):
    pass


class IncompleteRequest(AnalytixError):
    pass


class InvalidRequest(AnalytixError):
    pass
