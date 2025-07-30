"""Functions related to arguments."""

import inspect
import types


def validate_args(func: types.FunctionType, arguments: list[str]) -> None:
    """Validate call arguments for a given function or method.

    This function checks that all arguments specified in `arguments` are present in the function
    signature of `func`. If any of the specified arguments are not present in the function
    signature, the function raises a `TypeError` with a descriptive error
    message.

    Parameters
    ----------
    func : callable
        The function whose signature should be checked.
    arguments : list[str]
        A list of argument names to check for presence in the function signature.

    Raises
    ------
    TypeError
        If any of the arguments specified in `arguments` are not present in the function signature.
    """
    sig = inspect.signature(func)

    invalid_args: list[str] = []
    for arg in arguments:
        if arg not in sig.parameters:
            invalid_args.append(arg)

    if invalid_args:
        msg = f"Invalid arguments '{invalid_args}' specified in arguments of function '{func.__module__}.{func.__name__}'"
        raise TypeError(msg)
