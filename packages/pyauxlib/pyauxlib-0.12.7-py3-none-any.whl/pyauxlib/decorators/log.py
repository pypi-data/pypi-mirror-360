"""Log execution of functions and methods."""

import logging
from collections.abc import Callable
from typing import Any

import wrapt


def log(logger: logging.Logger, message: str, ending: bool = False) -> Any:
    """Log the start and end execution of a function or method.

    Parameters
    ----------
    logger : Logger
        Instance of the logger.
    message : str
        Indicate the function or method being executed
    ending : bool
        Show the end message
    """

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[..., Any],
        instance: Any | None,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        start_message = f"'{message}' started"
        separator_start = "-" * len(start_message)
        logger.info(separator_start)
        logger.info(start_message)

        result = wrapped(*args, **kwargs)

        if ending:
            end_message = f"'{message}' finished"
            logger.info(end_message)
            separator_end = "=" * len(end_message)
        else:
            separator_end = "=" * len(start_message)
        logger.info(separator_end)

        return result

    return wrapper
