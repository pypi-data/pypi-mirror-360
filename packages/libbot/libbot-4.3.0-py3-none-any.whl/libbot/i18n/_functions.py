from os import listdir, PathLike
from pathlib import Path
from typing import Any, Dict, List

from ..utils.config import config_get
from ..utils.json import json_read
from ..utils.syncs import asyncable


def _get_valid_locales(locales_root: str | PathLike[str]) -> List[str]:
    return [".".join(entry.split(".")[:-1]) for entry in listdir(locales_root)]


@asyncable
def _(
    key: str,
    *args: str,
    locale: str | None = "en",
    locales_root: str | Path = Path("locale"),
) -> Any:
    """Get value of locale string

    ### Args:
        * key (`str`): The last key of the locale's keys path.
        * *args (`str`): Path to key like: `dict[args][key]`.
        * locale (`str | None`): Locale to looked up in. Defaults to `"en"`.
        * locales_root (`str | Path`, *optional*): Folder where locales are located. Defaults to `Path("locale")`.

    ### Returns:
        * `Any`: Value of provided locale key. Is usually `str`, `Dict[str, Any]` or `List[Any]`
    """
    if locale is None:
        locale: str = config_get("locale")

    try:
        this_dict: Dict[str, Any] = json_read(Path(f"{locales_root}/{locale}.json"))
    except FileNotFoundError:
        try:
            this_dict: Dict[str, Any] = json_read(Path(f'{locales_root}/{config_get("locale")}.json'))
        except FileNotFoundError:
            return f'⚠️ Locale in config is invalid: could not get "{key}" in {args} from locale "{locale}"'

    this_key: Dict[str, Any] = this_dict

    for dict_key in args:
        this_key = this_key[dict_key]

    try:
        return this_key[key]
    except KeyError:
        return f'⚠️ Locale in config is invalid: could not get "{key}" in {args} from locale "{locale}"'


@_.asynchronous
async def _(
    key: str,
    *args: str,
    locale: str | None = "en",
    locales_root: str | Path = Path("locale"),
) -> Any:
    """Get value of locale string

    ### Args:
        * key (`str`): The last key of the locale's keys path.
        * *args (`str`): Path to key like: `dict[args][key]`.
        * locale (`str | None`): Locale to looked up in. Defaults to `"en"`.
        * locales_root (`str | Path`, *optional*): Folder where locales are located. Defaults to `Path("locale")`.

    ### Returns:
        * `Any`: Value of provided locale key. Is usually `str`, `Dict[str, Any]` or `List[Any]`
    """
    locale: str = config_get("locale") if locale is None else locale

    try:
        this_dict: Dict[str, Any] = await json_read(Path(f"{locales_root}/{locale}.json"))
    except FileNotFoundError:
        try:
            this_dict: Dict[str, Any] = await json_read(
                Path(f'{locales_root}/{await config_get("locale")}.json')
            )
        except FileNotFoundError:
            return f'⚠️ Locale in config is invalid: could not get "{key}" in {args} from locale "{locale}"'

    this_key: Dict[str, Any] = this_dict

    for dict_key in args:
        this_key = this_key[dict_key]

    try:
        return this_key[key]
    except KeyError:
        return f'⚠️ Locale in config is invalid: could not get "{key}" in {args} from locale "{locale}"'


@asyncable
def in_all_locales(key: str, *args: str, locales_root: str | Path = Path("locale")) -> List[Any]:
    """Get value of the provided key and path in all available locales

    ### Args:
        * key (`str`): The last key of the locale's keys path.
        * *args (`str`): Path to key like: `dict[args][key]`.
        * locales_root (`str | Path`, *optional*): Folder where locales are located. Defaults to `Path("locale")`.

    ### Returns:
        * `List[Any]`: List of values in all locales
    """

    output: List[Any] = []

    for locale in _get_valid_locales(locales_root):
        try:
            this_dict: Dict[str, Any] = json_read(Path(f"{locales_root}/{locale}.json"))
        except FileNotFoundError:
            continue

        this_key: Dict[str, Any] = this_dict

        for dict_key in args:
            this_key = this_key[dict_key]

        try:
            output.append(this_key[key])
        except KeyError:
            continue

    return output


@in_all_locales.asynchronous
async def in_all_locales(key: str, *args: str, locales_root: str | Path = Path("locale")) -> List[Any]:
    """Get value of the provided key and path in all available locales

    ### Args:
        * key (`str`): The last key of the locale's keys path.
        * *args (`str`): Path to key like: `dict[args][key]`.
        * locales_root (`str | Path`, *optional*): Folder where locales are located. Defaults to `Path("locale")`.

    ### Returns:
        * `List[Any]`: List of values in all locales
    """

    output: List[Any] = []

    for locale in _get_valid_locales(locales_root):
        try:
            this_dict: Dict[str, Any] = await json_read(Path(f"{locales_root}/{locale}.json"))
        except FileNotFoundError:
            continue

        this_key: Dict[str, Any] = this_dict

        for dict_key in args:
            this_key = this_key[dict_key]

        try:
            output.append(this_key[key])
        except KeyError:
            continue

    return output


@asyncable
def in_every_locale(
    key: str, *args: str, locales_root: str | Path = Path("locale")
) -> Dict[str, Any]:
    """Get value of the provided key and path in every available locale with locale tag

    ### Args:
        * key (`str`): The last key of the locale's keys path.
        * *args (`str`): Path to key like: `dict[args][key]`.
        * locales_root (`str | Path`, *optional*): Folder where locales are located. Defaults to `Path("locale")`.

    ### Returns:
        * `Dict[str, Any]`: Locale is a key, and it's value from locale file is a value
    """

    output: Dict[str, Any] = {}

    for locale in _get_valid_locales(locales_root):
        try:
            this_dict: Dict[str, Any] = json_read(Path(f"{locales_root}/{locale}.json"))
        except FileNotFoundError:
            continue

        this_key: Dict[str, Any] = this_dict

        for dict_key in args:
            this_key = this_key[dict_key]

        try:
            output[locale] = this_key[key]
        except KeyError:
            continue

    return output


@in_every_locale.asynchronous
async def in_every_locale(
    key: str, *args: str, locales_root: str | Path = Path("locale")
) -> Dict[str, Any]:
    """Get value of the provided key and path in every available locale with locale tag

    ### Args:
        * key (`str`): The last key of the locale's keys path.
        * *args (`str`): Path to key like: `dict[args][key]`.
        * locales_root (`str | Path`, *optional*): Folder where locales are located. Defaults to `Path("locale")`.

    ### Returns:
        * `Dict[str, Any]`: Locale is a key, and it's value from locale file is a value
    """

    output: Dict[str, Any] = {}

    for locale in _get_valid_locales(locales_root):
        try:
            this_dict: Dict[str, Any] = await json_read(Path(f"{locales_root}/{locale}.json"))
        except FileNotFoundError:
            continue

        this_key: Dict[str, Any] = this_dict

        for dict_key in args:
            this_key = this_key[dict_key]

        try:
            output[locale] = this_key[key]
        except KeyError:
            continue

    return output
