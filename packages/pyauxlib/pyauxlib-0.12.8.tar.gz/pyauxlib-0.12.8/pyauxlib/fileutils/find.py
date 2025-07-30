"""Find related functions."""

from pathlib import Path


def find_file(
    paths: list[Path],
    target_filename: str,
    extensions: list[str] | None = None,
    recursive: bool = True,
) -> Path | None:
    """Find a file within a list of directories.

    Search for a file in a list of directories, matching the target_filename with any of the
    provided extensions (including no extension if specified). Optionally, search can be recursive
    or non-recursive. The search is case-insensitive.

    Parameters
    ----------
    paths : list of pathlib.Path
        List of directory paths to search, processed in the given order.
    target_filename : str
        The base name of the file to find.
    extensions : list of str, optional
        List of file extensions to search for. If None, no extensions are assumed.
        Default is None.
    recursive : bool, optional
        If True, the search includes subdirectories. If False, only the top-level directories in
        `paths` are searched. Default is True.

    Returns
    -------
    pathlib.Path or None
        The path to the found file, or None if no matching file is found.

    Examples
    --------
    Search recursively for a file named 'config', 'config.yaml', or 'config.yml' in the specified
    directories:

    >>> from pathlib import Path
    >>> paths = [Path("/some/directory"), Path("/another/directory")]
    >>> find_file(paths, "config", ["", "yaml", "yml"], recursive=True)

    Search non-recursively for a file named 'data.txt' in the specified directories:

    >>> find_file(paths, "data", ["txt"], recursive=False)
    """
    extensions = extensions or [""]

    possible_filenames = {
        f"{target_filename.lower()}{f'.{ext.lower()}' if ext else ''}" for ext in extensions
    }

    # Search each path recursively
    for path in paths:
        if path.is_dir():
            search_iter = path.rglob("*") if recursive else path.glob("*")
            for file in search_iter:
                if file.name.lower() in possible_filenames:
                    return file
    return None
