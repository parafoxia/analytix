from .errors import InvalidRequest, UtilityError
from .youtube import api


def report_type_for(dimensions=(), metrics=(), filters={}, *, verify=False):
    r = api.reports.determine(dimensions, metrics, filters)

    if not verify:
        return r

    try:
        r().verify(dimensions, metrics, filters, 25, ("views",))
        return r
    except InvalidRequest as exc:
        return exc


def valid_filter_values_for(key):
    opts = api.valid.VALID_FILTER_OPTIONS.get(key, None)

    if not opts:
        raise UtilityError(f"'{key}' is not a valid filter")

    return opts


def valid_features_for(rtype):
    r = rtype()
    return {
        "Dimensions": r.dimensions.every,
        "Metrics": r.metrics.values,
        "Filters": r.filters.every,
    }
