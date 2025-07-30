"""Module providing the Timer class for measuring and logging execution times."""

import contextlib
import csv
import io
import logging
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar, Literal, Protocol

import wrapt

try:
    from typing import Self  # Only works from Python 3.11
except ImportError:
    from typing_extensions import Self


class TimeFunc(Protocol):
    """Protocol for functions that return the current time as a float."""

    def __call__(self) -> float:
        """Get the current time.

        Returns
        -------
        float
            The current time.
        """
        ...


class Timer:
    """Timer class to measure execution times.

    The timer can be managed in three ways:

    1. Manually, by calling the `start`, `stop`, etc. methods.
    2. As a context manager, which automatically starts the timer when entering the context and
    stops it when exiting.
    3. As a decorator, which times the execution of the decorated function. The helper function
    'pyauxlib.decorators.timer' simplifies the use as decorator (see the example below).

    Parameters
    ----------
    filename : str | Path | None
        The name or path of the file to save the timestamps.
    time_func : {"time", "perf_counter", "process_time"} | callable, optional
        The time function to use. It can be one of {"time", "perf_counter",
        "process_time"} or a custom time function. By default "time".
    logger : logging.Logger, optional
        The logger to use for logging warnings and elapsed time. By default None.

    Attributes
    ----------
    filename : str | Path | None
        The name of the file to save the timestamps. By default None.
    start_time : float or None
        The start time of the timer.
    stop_time : float or None
        The stop time of the timer.
    elapsed_time : float or None
        Total elapsed time (stop_time - start_time)
    timestamps : list of float
        The list of timestamps added during the timer execution.
    texts : list of str
        The list of texts associated with each timestamp.

    Methods
    -------
    start():
        Start the timer.

    stop():
        Stop the timer and returns the elapsed time. It also saves the timestamps to a file, when
        provided.

    add_timestamp(text):
        Add a timestamp with an associated text.

    save(filename):
        Save the timestamps and their associated texts to a file.

    reset():
        Reset the timer.

    get_data():
        Get the timer data as a list of rows.

    Examples
    --------
    Example usage:

    ```python
    >>> # Manual usage
    >>> t = Timer()
    >>> t.start()
    >>> # code here
    >>> elapsed = t.stop()
    >>> isinstance(elapsed, float)
    True
    >>> elapsed >= 0
    True


    >>> # Context manager usage
    >>> with Timer() as t:
    ...     # code here
    ...     t.add_timestamp("#1")
    ...     # more code
    ...     # The timer will automatically be stopped when exiting the context manager

    >>> # Decorator usage
    >>> timer = Timer()
    >>> @timer
    ... def some_function():
    ...     # function code
    ...     pass

    # Decorator usage with 'timer' helper function
    from pyauxlib.decorators.timer import timer

    @timer(filename='timer.txt')
    def some_function():
        # function code
    ```
    """

    TIME_FUNC: ClassVar[dict[str, TimeFunc]] = {
        "time": time.time,
        "perf_counter": time.perf_counter,
        "process_time": time.process_time,
    }

    def __init__(
        self,
        filename: str | Path | None = None,
        time_func: Literal["time", "perf_counter", "process_time"] | TimeFunc = "time",
        logger: logging.Logger | None = None,
    ):
        self.filename = Path(filename) if filename is not None else None

        if isinstance(time_func, str):
            self.time_func = self.TIME_FUNC[time_func]
        else:
            self.time_func = time_func

        self.logger = logging.getLogger(__name__) if logger is None else logger
        self.where_output = None if logger is None else logger.info
        self.running = False
        self.reset()

    def __enter__(self) -> Self:
        """Start a new timer as a context manager."""
        self.start()
        return self

    def __exit__(self, *exc_info: object) -> None:
        """Stop the context manager timer."""
        self.stop()

    @wrapt.decorator
    def __call__(
        self,
        wrapped: Callable[..., Any],
        instance: Any | None,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        """Measure the execution time of a decorated function or method."""
        self.reset()
        self.start()
        result = wrapped(*args, **kwargs)
        elapsed_time = self.stop()
        if self.logger is not None:
            self.logger.info("Elapsed time: %f s", elapsed_time)
        return result

    def start(self) -> None:
        """Start the timer."""
        if hasattr(self, "stop_time"):
            self.logger.warning("Timer has not been resetted.")
            return
        self.running = True
        self.add_timestamp("start")
        self.start_time = self.timestamps[-1]

    def stop(self, filename: str | Path | None = None) -> float:
        """Stop the timer and returns the elapsed time.

        It also saves the timestamps to a file, when provided or existing in the Timer class.
        """
        if not hasattr(self, "start_time"):
            self.logger.warning("Timer has not been started.")
            return 0

        self.add_timestamp("stop")
        self.stop_time = self.timestamps[-1]
        self.running = False
        self.save(filename)
        elapsed_time = self.stop_time - self.start_time
        self.elapsed_time = elapsed_time

        if self.where_output is not None:
            self.where_output(f"Elapsed time: {elapsed_time} s")

        return elapsed_time

    def add_timestamp(self, text: str = "") -> None:
        """Add a timestamp with an associated text.

        Parameters
        ----------
        text : str, optional
            The text associated with the timestamp. By default "".
        """
        if not self.running:
            self.logger.warning("Timer is not running.")

        self.timestamps.append(self.time_func())
        self.texts.append(text)

    def save(self, filename: str | Path | None = None) -> None:
        """Save the timestamps and their associated texts to a file.

        Parameters
        ----------
        filename : str | Path | None, optional
            The name or path of the file to save the timestamps to. If not provided,
            the filename attribute of the Timer object will be used. By default None.
        """
        if not hasattr(self, "start_time"):
            self.logger.warning("Timer has not been started.")
            return
        if not hasattr(self, "stop_time"):
            self.logger.warning("Timer has not been stopped yet.")
            return
        filename = filename or self.filename
        if filename is None:
            # NOTE Walrus operator fails in docstrings
            # if (filename := filename or self.filename) is None:
            return

        filename = Path(filename)

        with Path.open(filename, "w", newline="") as csvfile:
            csvfile.write(self._to_csv())

    def reset(self) -> None:
        """Reset the timer."""
        with contextlib.suppress(AttributeError):
            del self.start_time
            del self.stop_time
            del self.elapsed_time
        self.timestamps: list[float] = []
        self.texts: list[str] = []

    def get_data(self) -> list[list[str]]:
        """Get the timer data as a list of rows.

        This method returns the timer data, including the comment, timestamp, time,
        step time, and accumulated time for each timestamp, as a list of rows. The
        first row is the header.

        Returns
        -------
        list of list of str
            The timer data. Each inner list represents a row. The first row is the
            header.
        """
        rows = []
        header = ["Comment", "Timestamp", "Time", "Step Time", "Accumulated Time"]
        rows.append(header)

        prev_time = self.start_time
        for i, timestamp in enumerate(self.timestamps):
            elapsed_time = timestamp - prev_time
            total_time = timestamp - self.start_time
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            row = [
                self.texts[i],
                str(timestamp),
                formatted_time,
                str(elapsed_time),
                str(total_time),
            ]
            rows.append(row)
            prev_time = timestamp

        return rows

    def _to_csv(self) -> str:
        rows = self.get_data()

        # Convert rows to CSV string
        csv_str = io.StringIO()
        writer = csv.writer(csv_str)
        writer.writerows(rows)
        return csv_str.getvalue()

    def __str__(self) -> str:
        """Get the timer data as a printable string."""
        rows = self.get_data()

        # Compute column widths
        col_widths = [max(len(cell) for cell in col) for col in zip(*rows, strict=True)]

        # Format rows as table
        table_rows = []
        for row in rows:
            table_row = "  ".join(
                cell.ljust(width) for cell, width in zip(row, col_widths, strict=True)
            )
            table_rows.append(table_row)

        return "\n".join(table_rows)

    def __getattr__(self, name: str) -> Any:
        """Return the given attribute."""
        raise_error: str = ""
        if name == "start_time":
            raise_error = f"{name} is not set. Please start the timer first."
        elif name in {"stop_time", "elapsed_time"}:
            if hasattr(self, "start_time"):
                raise_error = f"{name} is not set. Please stop the timer first."
            else:
                raise_error = f"{name} is not set. Please start the timer first."
        if raise_error:
            raise AttributeError(raise_error)
