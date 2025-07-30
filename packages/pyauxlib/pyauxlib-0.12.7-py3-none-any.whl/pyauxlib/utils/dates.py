"""Functions related to dates and times."""

from datetime import datetime, timezone
from typing import Any

try:
    from dateutil import parser as date_parser
except ImportError:
    date_parser = None  # type: ignore[assignment]


def safe_strptime(
    value: str,
    fmt: str,
    default_tz: timezone | None = timezone.utc,
) -> datetime:
    """Parse a datetime string with optional default timezone assignment.

    If the parsed datetime is naive and `default_tz` is not None, the resulting datetime will have
    that timezone applied.

    Parameters
    ----------
    value : str
        The datetime string to parse.
    fmt : str
        The format string compatible with `datetime.strptime`.
    default_tz : Optional[timezone], default=timezone.utc
        The timezone to assign if the parsed datetime is naive (tzinfo is None). Use 'None' to not
        apply a timezone.

    Returns
    -------
    datetime
        The parsed datetime object, potentially with tzinfo set.

    Examples
    --------
    >>> safe_strptime("2023-09-27 16:37:54", "%Y-%m-%d %H:%M:%S")
    datetime.datetime(2023, 9, 27, 16, 37, 54, tzinfo=datetime.timezone.utc)

    >>> safe_strptime("2023-09-27 16:37:54", "%Y-%m-%d %H:%M:%S", default_tz=None)
    datetime.datetime(2023, 9, 27, 16, 37, 54)
    """
    dt = datetime.strptime(value, fmt)  # noqa: DTZ007
    if dt.tzinfo is None and default_tz is not None:
        dt = dt.replace(tzinfo=default_tz)
    return dt


def parse_date(value: Any, *, default_tz: timezone | None = timezone.utc) -> datetime:
    """Parse a datetime object or string in flexible formats, with optional timezone assignment.

    If the result is naive and `default_tz` is provided, the timezone will be applied.

    Parameters
    ----------
    value : Any
        A datetime object or string to parse.
    default_tz : Optional[timezone], default=timezone.utc
        The timezone to assign if the parsed datetime is naive. Use 'None' to not apply a timezone.

    Returns
    -------
    datetime
        A timezone-aware or naive `datetime` object, depending on input and flags.

    Raises
    ------
    ValueError
        If the input is not a string or datetime, or if parsing fails.

    Examples
    --------
    >>> parse_date("09/27/2023 16:37:54")
    datetime.datetime(2023, 9, 27, 16, 37, 54, tzinfo=datetime.timezone.utc)

    >>> parse_date("2023-09-27", default_tz=None)
    datetime.datetime(2023, 9, 27, 0, 0)
    """
    if isinstance(value, datetime):
        if value.tzinfo is None and default_tz is not None:
            return value.replace(tzinfo=default_tz)
        return value

    if isinstance(value, str):
        if date_parser is not None:
            try:
                dt = date_parser.parse(value)
                if dt.tzinfo is None and default_tz is not None:
                    dt = dt.replace(tzinfo=default_tz)
            except (ValueError, TypeError):
                pass
            else:
                return dt

        # Fallback to manual parsing for specific formats
        formats_to_try = [
            "%m/%d/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
        ]

        for fmt in formats_to_try:
            try:
                return safe_strptime(value, fmt, default_tz=default_tz)
            except ValueError:
                continue

        msg = f"Unable to parse date: {value!r}"
        raise ValueError(msg)

    msg = f"Expected string or datetime, got {type(value)}"
    raise ValueError(msg)
