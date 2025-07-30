"""Functions related to dictionaries."""

from typing import Any


def remove_keys(dictionary: dict[Any, Any], remove: str | list[str] | tuple[str]) -> dict[Any, Any]:
    """Remove the keys from a dictionary specified in the list `remove`.

    If an element from `remove` is not a key in `dict`, then it will ignore (won't raise
    any error)

    Parameters
    ----------
    dictionary : dict
        Original dictionary
    remove : str | list[str] | tuple[str]
        Keys to be removed from `dictionary`

    Returns
    -------
    dict
        Dictionary with the specified keys removed.
    """
    new_dict = dictionary.copy()
    if isinstance(remove, str):
        remove = [remove]
    for k in remove:
        new_dict.pop(k, None)

    return new_dict


def is_empty_or_none(dictionary: dict[Any, Any]) -> bool:
    """Check if a dictionary is empty or all its values are `None`.

    This function checks if a dictionary is empty or if all its values are `None`.
    It also checks nested dictionaries. A value of '0' is not considered empty.

    Parameters
    ----------
    dictionary : dict
        The dictionary to check.

    Returns
    -------
    bool
        True if the dictionary is empty or all its values are `None`, False otherwise.

    Examples
    --------
    ```python
    nested_dict = {'a': {'b': None, 'c': {}}}
    print(is_empty_or_none(nested_dict))
    # Output: True

    nested_dict = {'a': {'b': None, 'c': {'d': None}}}
    print(is_empty_or_none(nested_dict))
    # Output: True

    nested_dict = {'a': {'b': 0, 'c': {'d': None}}}
    print(is_empty_or_none(nested_dict))
    # Output: False
    ```
    """
    if not dictionary:
        return True

    for v in dictionary.values():
        if isinstance(v, dict):
            if not is_empty_or_none(v):
                return False
        elif v is not None:
            return False

    return True
