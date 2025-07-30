from pathlib import Path
from typing import Any, Dict

from ..json import json_read, json_write
from ..misc import nested_delete, nested_set
from ..syncs import asyncable

try:
    from ujson import dumps, loads
except ImportError:
    from json import dumps, loads

DEFAULT_CONFIG_LOCATION: str = "config.json"


@asyncable
def config_get(key: str, *path: str, config_file: str | Path = DEFAULT_CONFIG_LOCATION) -> Any:
    """Get a value of the config key by its path provided
    For example, `foo.bar.key` has a path of `"foo", "bar"` and the key `"key"`

    ### Args:
        * key (`str`): Key that contains the value
        * *path (`str`): Path to the key that contains the value (pass *[] or don't pass anything at all to get on the top/root level)
        * config_file (`str | Path`, *optional*): Path-like object or path as a string of a location of the config file. Defaults to `"config.json"`

    ### Returns:
        * `Any`: Key's value

    ### Example:
    Get the "salary" of "Pete" from this JSON structure:
    ```json
    {
        "users": {
            "Pete": {
                "salary": 10.0
            }
        }
    }
    ```

    This can be easily done with the following code:
    ```python
    import libbot
    salary = libbot.sync.config_get("salary", "users", "Pete")
    ```
    """
    this_key: Dict[str, Any] = json_read(config_file)

    for dict_key in path:
        this_key = this_key[dict_key]

    return this_key[key]


@config_get.asynchronous
async def config_get(key: str, *path: str, config_file: str | Path = DEFAULT_CONFIG_LOCATION) -> Any:
    """Get a value of the config key by its path provided
    For example, `foo.bar.key` has a path of `"foo", "bar"` and the key `"key"`

    ### Args:
        * key (`str`): Key that contains the value
        * *path (`str`): Path to the key that contains the value (pass *[] or don't pass anything at all to get on the top/root level)
        * config_file (`str | Path`, *optional*): Path-like object or path as a string of a location of the config file. Defaults to `"config.json"`

    ### Returns:
        * `Any`: Key's value

    ### Example:
    Get the "salary" of "Pete" from this JSON structure:
    ```json
    {
        "users": {
            "Pete": {
                "salary": 10.0
            }
        }
    }
    ```

    This can be easily done with the following code:
    ```python
    import libbot
    salary = await libbot.config_get("salary", "users", "Pete")
    ```
    """
    this_key: Dict[str, Any] = await json_read(config_file)

    for dict_key in path:
        this_key = this_key[dict_key]

    return this_key[key]


@asyncable
def config_set(key: str, value: Any, *path: str, config_file: str | Path = DEFAULT_CONFIG_LOCATION) -> None:
    """Set config's key by its path to the value

    ### Args:
        * key (`str`): Key that leads to the value
        * value (`Any`): Any JSON serializable data
        * *path (`str`): Path to the key of the target (pass *[] or don't pass anything at all to set on the top/root level)
        * config_file (`str | Path`, *optional*): Path-like object or path as a string of a location of the config file. Defaults to `"config.json"`

    ### Raises:
        * `KeyError`: Key is not found under path provided
    """
    json_write(nested_set(json_read(config_file), value, *(*path, key)), config_file)


@config_set.asynchronous
async def config_set(
    key: str, value: Any, *path: str, config_file: str | Path = DEFAULT_CONFIG_LOCATION
) -> None:
    """Set config's key by its path to the value

    ### Args:
        * key (`str`): Key that leads to the value
        * value (`Any`): Any JSON serializable data
        * *path (`str`): Path to the key of the target (pass *[] or don't pass anything at all to set on the top/root level)
        * config_file (`str | Path`, *optional*): Path-like object or path as a string of a location of the config file. Defaults to `"config.json"`

    ### Raises:
        * `KeyError`: Key is not found under path provided
    """
    await json_write(nested_set(await json_read(config_file), value, *(*path, key)), config_file)


@asyncable
def config_delete(
    key: str,
    *path: str,
    missing_ok: bool = False,
    config_file: str | Path = DEFAULT_CONFIG_LOCATION,
) -> None:
    """Set config's key by its path

    ### Args:
        * key (`str`): Key to delete
        * *path (`str`): Path to the key of the target (pass *[] or don't pass anything at all to delete on the top/root level)
        * missing_ok (`bool`): Do not raise an exception if the key is missing. Defaults to `False`
        * config_file (`str | Path`, *optional*): Path-like object or path as a string of a location of the config file. Defaults to `"config.json"`

    ### Raises:
        * `KeyError`: Key is not found under path provided and `missing_ok` is `False`
    """
    config_data: Dict[str, Any] = json_read(config_file)

    try:
        nested_delete(config_data, *(*path, key))
    except KeyError as exc:
        if not missing_ok:
            raise exc from exc

    json_write(config_data, config_file)


@config_delete.asynchronous
async def config_delete(
    key: str,
    *path: str,
    missing_ok: bool = False,
    config_file: str | Path = DEFAULT_CONFIG_LOCATION,
) -> None:
    """Set config's key by its path

    ### Args:
        * key (`str`): Key to delete
        * *path (`str`): Path to the key of the target (pass *[] or don't pass anything at all to delete on the top/root level)
        * missing_ok (`bool`): Do not raise an exception if the key is missing. Defaults to `False`
        * config_file (`str | Path`, *optional*): Path-like object or path as a string of a location of the config file. Defaults to `"config.json"`

    ### Raises:
        * `KeyError`: Key is not found under path provided and `missing_ok` is `False`
    """
    config_data: Dict[str, Any] = await json_read(config_file)

    try:
        nested_delete(config_data, *(*path, key))
    except KeyError as exc:
        if not missing_ok:
            raise exc from exc

    await json_write(config_data, config_file)
