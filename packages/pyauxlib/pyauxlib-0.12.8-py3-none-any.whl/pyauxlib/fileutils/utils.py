"""Utils for io."""


def clean_file_extension(extension: str) -> str:
    """Clean an extension file.

    Removes all characters before the '.' and makes the extension lowercase.
    Example: '*.PY' -> '.py'

    It adds the '.' in case it's not present
    """
    if not extension.startswith("."):
        extension = "." + extension
    return extension.lower()
