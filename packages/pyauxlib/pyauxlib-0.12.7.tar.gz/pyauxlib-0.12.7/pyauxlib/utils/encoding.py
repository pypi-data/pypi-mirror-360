"""Encoding-related functions."""

import logging
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

try:
    import chardet

    HAS_CHARDET = True
except ImportError:
    chardet = None  # type: ignore[assignment]
    HAS_CHARDET = False

logger = logging.getLogger(__name__)


def detect_encoding(file: str | Path) -> str | None:
    """Detect the encoding of a file by reading the first bytes.

    Parameters
    ----------
    file : str | Path
        file to be checked

    Returns
    -------
    encoding : str | None
        encoding of the file (None if file is not found, or no encoding can be detected)
    """
    codecs = {
        BOM_UTF8: "utf_8_sig",
        BOM_UTF16: "utf_16",
        BOM_UTF16_BE: "utf_16_be",
        BOM_UTF16_LE: "utf_16_le",
        BOM_UTF32: "utf_32",
        BOM_UTF32_BE: "utf_32_be",
        BOM_UTF32_LE: "utf_32_le",
        b"": "utf-8",
    }
    file_path = Path(file)
    try:
        with Path.open(file_path, "rb") as f:
            first_chars = f.read(max(len(bom) for bom in codecs))
            for bom, encoding in codecs.items():
                if first_chars.startswith(bom):
                    return encoding
    except FileNotFoundError as err:
        logger.warning("Error %s loading file: %s", err, file_path)
        return None
    else:
        # If no BOM is detected, try chardet if available
        if HAS_CHARDET:
            return detect_encoding_chardet(file_path)
        return None


def detect_encoding_chardet(file: str | Path) -> str | None:
    """Detect the encoding of a file using the chardet library.

    This function uses the chardet library to guess the encoding of a file based on heuristics.
    Note that this method may not always be accurate and can be slow for large files. It is
    recommended to use this function when other encoding detection methods fail.

    Parameters
    ----------
    file : str | Path
        The path of the file for which to detect the encoding.

    Returns
    -------
    str | None
        The detected encoding of the file, or None if the encoding could not be detected.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    AttributeError
        If the chardet library is not installed.

    Examples
    --------
    ```python
    encoding = detect_encoding_chardet("/path/to/file.txt")
    print(encoding)
    # Output: 'utf-8'
    ```
    """
    if chardet is None:
        logger.warning("Install package 'chardet' for additional encoding detection.")  # type: ignore[unreachable]
        return None
    file = Path(file) if isinstance(file, str) else file
    try:
        with Path.open(file, "rb") as f:
            result = chardet.detect(f.read())
            return result["encoding"]
    except FileNotFoundError:
        logger.warning("Error %s loading file", file)
        return None
