"""Utility functions for inspecting callable attributes of an object.

Functions
---------
public_callables(obj: object) -> list[str]
    Return the names of the public callable attributes of an object. Public attributes are those
    not starting with an underscore ("_"). A callable attribute could be a method (bound, unbound,
    static, or class) or any other callable object.
"""


def public_callables(obj: object) -> list[str]:
    """Return the public callable attributes of an object.

    Public attributes are those not starting with an underscore ("_").
    A callable attribute could be a method (bound, unbound, static, or class) or any other callable
    object.

    Parameters
    ----------
    obj : object
        The object to inspect.

    Returns
    -------
    list[str]
        List of public attribute names.
    """
    attrs = dir(obj)
    return [
        method for method in attrs if not method.startswith("_") and callable(getattr(obj, method))
    ]
