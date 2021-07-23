__all__ = (
    "PANDAS_AVAILABLE",
    "NUMPY_AVAILABLE",
    "requires_pandas",
    "requires_numpy",
)

from pkg_resources import working_set

from analytix.errors import MissingOptionalComponents

_packages = [p.key for p in working_set]
PANDAS_AVAILABLE = "pandas" in _packages
NUMPY_AVAILABLE = "numpy" in _packages


def requires_pandas(func):
    def wrapper(*args, **kwargs):
        if not PANDAS_AVAILABLE:
            raise MissingOptionalComponents("pandas is not installed")

        return func(*args, **kwargs)

    return wrapper


def requires_numpy(func):
    def wrapper(*args, **kwargs):
        if not NUMPY_AVAILABLE:
            raise MissingOptionalComponents("numpy is not installed")

        return func(*args, **kwargs)

    return wrapper
