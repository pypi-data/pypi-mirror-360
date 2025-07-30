"""Utilities for working with NetCDF files."""

import importlib.util
from typing import TYPE_CHECKING, Any, Literal, overload

if TYPE_CHECKING:
    from xarray.backends.api import T_NetcdfEngine


@overload
def get_netcdf_engine_and_encoding(
    compressed: Literal[True] = True,
) -> tuple["T_NetcdfEngine | None", dict[str, Any]]: ...
@overload
def get_netcdf_engine_and_encoding(
    compressed: Literal[False] = False,
) -> tuple["T_NetcdfEngine | None", None]: ...


def get_netcdf_engine_and_encoding(
    compressed: bool = True,
) -> tuple["T_NetcdfEngine | None", dict[str, Any] | None]:
    """Determine the available NetCDF engine and its corresponding encoding.

    This function checks if 'h5netcdf', 'netCDF4', or 'scipy' libraries are available. It returns
    the name of the library and a dictionary with the appropriate encoding settings.
    If neither library is available, it returns None for both the engine and encoding.

    Parameters
    ----------
    compressed : bool, optional
        Whether to return encoding for compression (default is True)

    Returns
    -------
    engine : str or None
        The name of the available NetCDF engine ('h5netcdf', 'netcdf4', or 'scipy'), or None
        if none are available.
    encoding : dict or None
        A dictionary with the appropriate encoding settings for the available engine, or None
        if no engine is available.
    """
    if importlib.util.find_spec("h5netcdf") is not None:
        return "h5netcdf", {"compression": "gzip", "compression_opts": 9} if compressed else None

    if importlib.util.find_spec("netCDF4") is not None:
        return "netcdf4", {"zlib": True, "complevel": 9} if compressed else None

    if importlib.util.find_spec("scipy") is not None:
        return "scipy", None  # scipy doesn't support compression in the same way

    return None, None
