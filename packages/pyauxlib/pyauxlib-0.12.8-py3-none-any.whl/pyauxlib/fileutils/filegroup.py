"""Management of groups of files with related names."""

from pathlib import Path


class FileGroup:
    """Manage groups of files with related names."""

    def __init__(self, directory: Path, base_name: str, suffix: str) -> None:
        """Initialize a file group handler for managing related files.

        This class helps manage multiple files that share a common base name but have different
        appendixes. For example, if you have files like 'report.pdf', 'report_draft.pdf',
        'report_final.pdf', you can use this class to easily generate paths for all of them.

        Parameters
        ----------
        directory : Path
            Directory containing the files. This can be an existing or non-existing directory
        base_name : str
            Base name of the files without suffix (e.g., 'report' for 'report.pdf')
        suffix : str
            File extension including the dot (e.g., '.pdf', '.zip')

        Examples
        --------
        >>> files = FileGroup(Path("docs"), "report", ".pdf")
        >>> files.get() # doctest: +SKIP
        Path("docs/report.pdf")
        >>> files.get("_draft")  # doctest: +SKIP
        Path("docs/report_draft.pdf")
        """
        self.directory = directory
        self.base = base_name
        self.suffix = suffix

    def get(self, append: str = "") -> Path:
        """Generate a Path object for a file with an optional appendix.

        This method creates a Path by combining the directory, base name, optional appendix,
        and suffix. The appendix is added between the base name and suffix.

        Parameters
        ----------
        append : str, optional
            String to append to the base name before the suffix. Common patterns include:
            - "_draft" for draft versions
            - "_bak" for backups
            - "_v1" for version numbers
            Default is an empty string, which returns the base file.

        Returns
        -------
        Path
            Complete path to the file, combining directory, base name, appendix, and suffix.
            Note: This method only creates the Path object, it doesn't check if the file exists
            or create it.

        Examples
        --------
        >>> fg = FileGroup(Path("data"), "users", ".csv")
        >>> fg.get() # doctest: +SKIP
        Path("data/users.csv")
        >>> fg.get("_2023") # doctest: +SKIP
        Path("data/users_2023.csv")
        >>> fg.get("_backup") # doctest: +SKIP
        Path("data/users_backup.csv")
        """
        name = f"{self.base}{append}{self.suffix}"
        return self.directory / name
