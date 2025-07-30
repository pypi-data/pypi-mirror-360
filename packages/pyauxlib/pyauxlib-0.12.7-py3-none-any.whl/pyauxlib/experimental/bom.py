"""Utilities for handling the Byte Order Mark (BOM) of files."""

from codecs import (
    BOM_UTF8,
    BOM_UTF16,
    BOM_UTF16_BE,
    BOM_UTF16_LE,
    BOM_UTF32,
    BOM_UTF32_BE,
    BOM_UTF32_LE,
)
from pathlib import Path

bom_codecs = [
    BOM_UTF8,
    BOM_UTF16,
    BOM_UTF16_BE,
    BOM_UTF16_LE,
    BOM_UTF32,
    BOM_UTF32_BE,
    BOM_UTF32_LE,
]


def remove_bom(filename: Path | str, output_filename: Path | str | None = None) -> None:
    """
    Remove the Byte Order Mark (BOM) from a file.

    Parameters
    ----------
    filename : str
        The path to the input file.
    output_filename : str, optional
        The path to the output file. If not provided, the input file will be overwritten.

    Raises
    ------
    FileNotFoundError
        If the input file does not exist.
    """
    filename = Path(filename)
    # Open the file in binary mode, read it in, and remove the BOM
    with Path.open(filename, "rb") as file:
        content = file.read()
    # Check if content starts with any of the BOMs and remove it
    for bom in bom_codecs:
        if content.startswith(bom):
            content = content[len(bom) :]
            break

    # Write the new content to a file
    output_filename = filename if output_filename is None else output_filename
    with Path.open(filename, "wb") as file:
        file.write(content)
