"""Handling of zip files."""

import zipfile
from collections.abc import Generator
from pathlib import Path
from typing import IO


def yield_files_from_zip(zip_path: str) -> Generator[tuple[Path, IO[bytes]], None, None]:
    """Yield files from a zip file.

    Parameters
    ----------
    zip_path : str
        The path to the zip file.

    Yields
    ------
    Tuple[Path, IO[bytes]]
        The path of the file and the file object.

    Examples
    --------
    >>> for path, file in yield_files_from_zip("example.zip"): # doctest: +SKIP
    ...     print(path, file)
    """
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        for filename in zip_file.namelist():
            with zip_file.open(filename) as file:
                yield Path(filename), file
