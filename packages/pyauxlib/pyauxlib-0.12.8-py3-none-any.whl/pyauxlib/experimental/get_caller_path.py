"""Experimental function to get the path of caller of a function."""

from inspect import currentframe, getframeinfo
from pathlib import Path
from types import FrameType

from pyauxlib.decorators.warning import experimental


@experimental
def get_caller_path() -> Path | None:
    """Get the path of the caller script.

    The 'caller' here is the caller of the script that called this one.

    Returns
    -------
    Path | None
        Path of the caller script (`None` if there is no caller)
    """
    # ??? Does this work as intended? Is it useful?

    # Gets the path of the calling script (must be the "main")

    # NOTE: 'f_back' twice
    # The 1st is for the script calling this one, the 2nd is for the script calling the
    # script that called this... which might be a NoneType

    try:
        if (current_frame := currentframe()) is None:
            return None
        parent_frame = current_frame.f_back
        if not isinstance(parent_frame, FrameType):
            return None
        grandparent_frame = parent_frame.f_back
        if not isinstance(grandparent_frame, FrameType):
            return None

        return Path(getframeinfo(grandparent_frame).filename)
    except AttributeError:
        # Handle case where there is no caller or caller's caller
        return None
