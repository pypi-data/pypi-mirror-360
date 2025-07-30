"""Decorators for handling imports."""

import importlib
import logging
from collections.abc import Callable
from typing import Any, TypeVar, cast

import wrapt

from pyauxlib.decorators.warning import deprecated

logger = logging.getLogger(__name__)


F = TypeVar("F", bound=Callable[..., Any])


# Cache to store dependency availability
OPTIONAL_DEPS: dict[str, bool] = {}


def check_dependency(dep_name: str, optional_deps: dict[str, bool] = OPTIONAL_DEPS) -> bool:
    """Check if a dependency is installed, with caching.

    This function checks whether a Python package is installed by attempting to find
    its module specification using `importlib.util.find_spec`. It caches the results
    in the `optional_deps` dictionary to avoid redundant checks in future calls.

    Parameters
    ----------
    dep_name : str
        The name of the dependency to check (e.g., "numpy", "pandas").
    optional_deps : dict[str, bool], optional
        A dictionary to store the cached results of dependency checks. Defaults to
            the global `OPTIONAL_DEPS` dictionary.

    Returns
    -------
    bool
        True if the dependency is available, False otherwise.

    Examples
    --------
        >>> OPTIONAL_DEPS = {}
        >>> check_dependency("wrapt", OPTIONAL_DEPS)
        True
        >>> check_dependency("nonexistent_package", OPTIONAL_DEPS)
        False
        >>> OPTIONAL_DEPS
        {'wrapt': True, 'nonexistent_package': False}
    """
    if dep_name not in OPTIONAL_DEPS:
        optional_deps[dep_name] = importlib.util.find_spec(dep_name) is not None
    return optional_deps[dep_name]


def require(*dependencies: str, raise_error: bool = True) -> Callable[[F], F]:
    """Check if required dependencies are installed.

    Parameters
    ----------
    *dependencies : str
        Names of the required dependencies.
    raise_error : bool, optional
        Whether to raise an ImportError if dependencies are missing.
        Defaults to True.

    Returns
    -------
    Callable[[F], F]
        A decorator to enforce dependency requirements.
        The decorator preserves the signature of the wrapped function.

    Examples
    --------
    >>> @require("numpy")
    ... def calculate_mean(data):
    ...     import numpy as np
    ...     return np.mean(data)

    >>> @require("sklearn", "yellowbrick", raise_error=False)
    ... def optional_silhouette(data):
    ...     try:
    ...         from sklearn.metrics import silhouette_score
    ...         from yellowbrick.cluster import SilhouetteVisualizer
    ...         # function implementation
    ...     except ImportError:
    ...         return None
    """

    @wrapt.decorator
    def wrapper(
        wrapped: F, instance: Any, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> Any | None:
        missing_deps = [dep for dep in dependencies if not check_dependency(dep)]
        if missing_deps:
            dep_list = ", ".join(missing_deps)
            func_name = f"{wrapped.__module__}.{wrapped.__qualname__}"
            error_msg = (
                f"Missing dependencies for '{func_name}': {dep_list}. "
                "Install them to use this function."
            )
            if raise_error:
                logger.exception(error_msg)
                raise ImportError(error_msg)
            logger.warning(error_msg)
            # Graceful degradation if `raise_error=False`
            return None
        return wrapped(*args, **kwargs)

    return cast(Callable[[F], F], wrapper)


@deprecated(reason="Use 'require' instead", since="0.11", removed="0.12", action="always")
def packages_required(package_names: list[str]) -> Any:
    """Check if specific packages are installed.

    Parameters
    ----------
    package_names : List[str]
        The names of the packages that the decorated function requires.

    Returns
    -------
    Callable[..., Any]
        The decorated function, which will raise an ImportError if the required packages are not
        installed.
    """
    return require(*package_names)


def require_class(*dependencies: str, raise_error: bool = True) -> Callable[[type[Any]], type[Any]]:
    """Class decorator to check for required dependencies.

    Parameters
    ----------
    *dependencies : str
        Names of the required dependencies.
    raise_error : bool, optional
        Whether to raise an ImportError if dependencies are missing.
        Defaults to True.

    Returns
    -------
    Callable[[type[Any]], type[Any]]
        A decorator that enforces dependency requirements for a class.
    """

    def class_decorator(cls: type[Any]) -> type[Any]:
        missing_deps = [dep for dep in dependencies if not check_dependency(dep)]

        if not missing_deps:
            return cls

        # Wrap the original `__init__` method
        @wrapt.decorator
        def init_wrapper(
            wrapped: Callable[..., None],
            instance: Any,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> None:
            dep_list = ", ".join(missing_deps)
            error_msg = (
                f"Missing dependencies for class '{cls.__name__}': '{dep_list}'. "
                "Install these dependencies to use this class."
            )
            if raise_error:
                raise ImportError(error_msg)

            # Proceed with the original constructor (does nothing if raise_error=True)
            logger.warning(error_msg)
            wrapped(*args, **kwargs)

        # Wrap the class's __init__ method
        setattr(cls, "__init__", init_wrapper(cls.__init__))  # noqa: B010
        return cls

    return class_decorator
