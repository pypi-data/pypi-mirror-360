"""Logging functions."""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from pyauxlib.fileutils.filesfolders import create_folder

if sys.version_info >= (3, 11):
    from datetime import UTC
else:
    # For Python 3.10
    from datetime import timezone

    UTC = timezone.utc


def _set_level(level: int | str | None, default_level: int | str = "INFO") -> int:
    """Return a correct logging level value.

    This function takes a logging level as input, which can be either an integer, a string, or None.
    If the level is a string, it should be one of the following:
        ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'].
    Note that lower case letters can also be used.

    If the level is None , the function will return the default_level.

    Parameters
    ----------
    level : int | str | None
        level of the logger, by "INFO"
        Any of the levels of logging can be passed as a string:
        ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        Note that lower case letters can also be used
    default_level : int | str, optional
        default level in case that `level` is incorrect, by default "INFO"

    Returns
    -------
    int
        The numeric value of the logging level.

    Raises
    ------
    ValueError
        If the level string is not a valid logging level.
    TypeError
        If the level is not None, int, or str.
    """
    if level is None:
        level = default_level

    if isinstance(level, int):
        return level

    try:
        return logging._nameToLevel[level.upper()]  # noqa: SLF001
    except KeyError as err:
        valid_levels = ", ".join(logging._nameToLevel.keys())  # noqa: SLF001
        error_msg = f"Invalid logging level: {level}. Valid levels are: {valid_levels}"
        raise ValueError(error_msg) from err


def init_logger(  # noqa: PLR0913
    name: str,
    level: int | str = "INFO",
    level_console: int | str | None = None,
    level_file: int | str | None = None,
    output_folder: Path | None = None,
    file_size: int = 1024 * 1024,
    propagate: bool = False,
    output_console: bool = True,
    colored_console: bool = True,
    output_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """Initialize the logger with enhanced features.

    Parameters
    ----------
    name : str
        Name of the logger.
    level : int or str, optional
        Overall logging level, by default "INFO".
        Any of the levers of logging can be passed as a string:
        ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        Note that lower case letters can also be used.
    level_console : int or str or None, optional
        Console logging level, by default None.
    level_file : int or str or None, optional
        File logging level, by default None.
    output_folder : Path or None, optional
        Folder to save log files, by default None.
    file_size : int, optional
        Maximum size of log files before rotation, by default 1MB.
    propagate : bool, optional
        Whether to propagate logs to parent loggers, by default False.
    output_console : bool, optional
        Whether to output logs to console, by default True.
    colored_console : bool, optional
        Use colors in the console output
    output_format : str, optional
        Format string for log messages, by default:
        "%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s".

    Returns
    -------
    logging.Logger
        Configured logger instance.

    Raises
    ------
    ValueError
        If an invalid logging level is provided.
    """
    logger = logging.getLogger(name)
    try:
        level = _set_level(level)
        level_console = _set_level(level_console, default_level=level)
        level_file = _set_level(level_file, default_level=level)
    except (ValueError, TypeError) as e:
        error_msg = f"Invalid logging level: {e!s}"
        raise ValueError(error_msg) from e

    level = min([level, level_console, level_file])

    logger.setLevel(level=level)
    logger.propagate = propagate

    formatter = logging.Formatter(output_format)

    if output_folder is not None:
        create_folder(output_folder, includes_file=False)
        timestamp = datetime.now(tz=UTC).astimezone().strftime("%Y%m%d_%H%M%S")
        log_file = output_folder / f"{name}_{timestamp}.log"

        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file, maxBytes=file_size, backupCount=5
        )
        file_handler.setLevel(level_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if output_console:

        class ColorFormatter(logging.Formatter):
            """Logging formatter adding console colors to the output."""

            COLORS: ClassVar[dict[str, str]] = {
                "DEBUG": "\033[0;36m",  # Cyan
                "INFO": "\033[0;32m",  # Green
                "WARNING": "\033[0;33m",  # Yellow
                "ERROR": "\033[0;31m",  # Red
                "CRITICAL": "\033[0;35m",  # Magenta
                "RESET": "\033[0m",  # Reset
            }

            def format(self, record: logging.LogRecord) -> str:
                """Format the specified record as text.

                Parameters
                ----------
                record : logging.LogRecord
                    The log record to format.

                Returns
                -------
                str
                    The formatted log record with color codes.
                """
                log_message = super().format(record)
                return f"{self.COLORS.get(record.levelname, self.COLORS['RESET'])}{log_message}{self.COLORS['RESET']}"

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level_console)
        if colored_console:
            console_handler.setFormatter(ColorFormatter(output_format))
        else:
            console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
