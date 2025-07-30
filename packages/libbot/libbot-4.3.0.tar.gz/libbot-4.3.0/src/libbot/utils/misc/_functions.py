import inspect
from typing import Any, Dict
from typing import Callable


def supports_argument(func: Callable[..., Any], arg_name: str) -> bool:
    """Check whether a function has a specific argument

    ### Args:
        * func (`Callable[..., Any]`): Function to be inspected
        * arg_name (`str`): Argument to be checked

    ### Returns:
        * `bool`: `True` if argument is supported and `False` if not
    """
    if hasattr(func, "__code__"):
        return arg_name in inspect.signature(func).parameters

    if hasattr(func, "__doc__"):
        if doc := func.__doc__:
            first_line = doc.splitlines()[0]
            return arg_name in first_line

    return False


def nested_set(
    target: Dict[str, Any], value: Any, *path: str, create_missing: bool = True
) -> Dict[str, Any]:
    """Set the key by its path to the value

    ### Args:
        * target (`Dict[str, Any]`): Dictionary to perform modifications on
        * value (`Any`): Any data
        * *path (`str`): Path to the key of the target
        * create_missing (`bool`, *optional*): Create keys on the way if they're missing. Defaults to `True`

    ### Raises:
        * `KeyError`: Key is not found under path provided

    ### Returns:
        * `Dict[str, Any]`: Changed dictionary
    """
    target_copy: Dict[str, Any] = target

    for key in path[:-1]:
        if key in target_copy:
            target_copy = target_copy[key]
        elif create_missing:
            target_copy = target_copy.setdefault(key, {})
        else:
            raise KeyError(
                f"Key '{key}' is not found under path provided ({path}) and create_missing is False"
            )

    if path[-1] in target_copy or create_missing:
        target_copy[path[-1]] = value

    return target


def nested_delete(target: Dict[str, Any], *path: str) -> Dict[str, Any]:
    """Delete the key by its path

    ### Args:
        * target (`Dict[str, Any]`): Dictionary to perform modifications on

    ### Raises:
        * `KeyError`: Key is not found under path provided

    ### Returns:
        `Dict[str, Any]`: Changed dictionary
    """
    target_copy: Dict[str, Any] = target

    for key in path[:-1]:
        if key in target_copy:
            target_copy = target_copy[key]
        else:
            raise KeyError(f"Key '{key}' is not found under path provided ({path})")

    if path[-1] in target_copy:
        del target_copy[path[-1]]
    else:
        raise KeyError(f"Key '{path[-1]}' is not found under path provided ({path})")

    return target
