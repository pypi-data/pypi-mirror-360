"""Timer decorator."""

import logging
from pathlib import Path
from typing import Any, Literal

from pyauxlib.utils.timer import TimeFunc, Timer


def timer(
    filename: str | Path | None = None,
    time_func: Literal["time", "perf_counter", "process_time"] | TimeFunc = "time",
    logger: logging.Logger | None = None,
) -> Any:
    """Measure the execution of functions or methods.

    This decorator creates a Timer instance and uses it to measure the execution time of the
    decorated function or method. The timestamps are saved to a file if a filename is provided.

    Parameters
    ----------
    filename : str | Path | None, optional
        The name or path of the file to save the timestamps. By default None.
    time_func : {"time", "perf_counter", "process_time"} | callable, optional
        The time function to use. It can be one of {"time", "perf_counter",
        "process_time"} or a custom time function. By default "time".
    logger : logging.Logger, optional
        The logger to use for logging warnings. By default None.

    Returns
    -------
    callable
        The decorated function or method.

    Examples
    --------
    Here's how you can use this decorator:

    ```python
    @timer()
    def some_function():
        # function code

    # Or with arguments
    @timer(filename='timer.txt')
    def some_function():
        # function code
    ```

    In this example, `some_function` is timed and the timestamps are saved to 'timer.txt'.
    """
    return Timer(filename=filename, time_func=time_func, logger=logger)
