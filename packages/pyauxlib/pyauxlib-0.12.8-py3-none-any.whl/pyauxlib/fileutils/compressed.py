"""Utils related to compressing."""

import logging
import shutil
from collections.abc import Callable
from pathlib import Path

from pyauxlib.utils.dates import get_local_time

logger = logging.getLogger(__name__)


def generate_alternative_name(file: Path, attempt: int = 1) -> Path:
    """Generate an alternative file name using a timestamp and attempt number.

    Parameters
    ----------
    file : Path
        Original file path.
    attempt : int, optional
        Attempt number (default is 1).

    Returns
    -------
    Path
        New file path with timestamp and attempt number.
    """
    timestamp = get_local_time().strftime("%Y%m%d%H%M%S")
    return file.with_stem(f"{file.stem}_BAK_{timestamp}_{attempt}")


def make_compressed_file(  # noqa: PLR0913
    file: Path,
    root_dir: str | Path,
    compressed_format: str = "zip",
    retry: bool = True,
    max_attempts: int = 5,
    alternative_namer: Callable[[Path, int], Path] = generate_alternative_name,
) -> None:
    """Handle the case of PermissionError when saving a compressed file.

    This function attempts to create a compressed archive of the specified root directory. If a
    PermissionError occurs and retry is True, it will attempt to save the file with an alternative
    name using the provided naming function.

    Parameters
    ----------
    file : Path
        Path of the output compressed file (without extension).
    root_dir : str | Path
        Directory that needs to be compressed.
    compressed_format : str, optional
        Format of the compressed file (default is "zip").
    retry : bool, optional
        Whether to retry with an alternative name in case of PermissionError (default is True).
    max_attempts : int, optional
        Maximum number of retry attempts (default is 5).
    alternative_namer : callable, optional
        Function to generate alternative file names (default is 'generate_alternative_name').
        It should take a Path object and an attempt number as arguments and return a new Path.

    Returns
    -------
    None

    Raises
    ------
    PermissionError
        If unable to save the file and retry is False.

    Notes
    -----
    The function will print status messages to inform about any PermissionErrors and alternative
    saving attempts.
    """
    attempt = 1
    current_file = file

    while attempt <= max_attempts:
        try:
            shutil.make_archive(str(current_file), format=compressed_format, root_dir=root_dir)
            if attempt > 1:
                msg = f"Successfully saved compressed file to '{current_file}.{compressed_format}'"
                logger.info(msg)

        except PermissionError as err:
            if retry and attempt < max_attempts:
                current_file = alternative_namer(file, attempt)
                msg = (
                    f"PermissionError: Can't save to file '{file}.{compressed_format}'."
                    f"Attempting to save to '{current_file}.{compressed_format}' (Attempt {attempt}/{max_attempts})"
                )
                logger.warning(msg)
                attempt += 1
            else:
                msg = f"PermissionError: Can't save to file {current_file}.{compressed_format} after {attempt} attempts"
                logger.exception(msg)
                raise PermissionError(msg) from err
        else:
            return
