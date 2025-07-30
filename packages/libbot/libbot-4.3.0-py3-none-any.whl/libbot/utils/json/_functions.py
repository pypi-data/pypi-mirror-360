from pathlib import Path
from typing import Any

import aiofiles

from ..misc import supports_argument
from ..syncs import asyncable

try:
    from ujson import dumps, loads
except ImportError:
    from json import dumps, loads


@asyncable
def json_read(path: str | Path) -> Any:
    """Read contents of a JSON file

    ### Args:
        * path (`str | Path`): Path-like object or path as a string

    ### Returns:
        * `Any`: File contents
    """
    with open(str(path), mode="r", encoding="utf-8") as f:
        data = f.read()

    return loads(data)


@json_read.asynchronous
async def json_read(path: str | Path) -> Any:
    """Read contents of a JSON file

    ### Args:
        * path (`str | Path`): Path-like object or path as a string

    ### Returns:
        * `Any`: File contents
    """
    async with aiofiles.open(str(path), mode="r", encoding="utf-8") as f:
        data = await f.read()

    return loads(data)


@asyncable
def json_write(data: Any, path: str | Path) -> None:
    """Write contents to a JSON file

    ### Args:
        * data (`Any`): Contents to write. Must be a JSON serializable
        * path (`str | Path`): Path-like object or path as a string of a destination
    """
    with open(str(path), mode="w", encoding="utf-8") as f:
        f.write(
            dumps(data, ensure_ascii=False, escape_forward_slashes=False, indent=4)
            if supports_argument(dumps, "escape_forward_slashes")
            else dumps(data, ensure_ascii=False, indent=4)
        )


@json_write.asynchronous
async def json_write(data: Any, path: str | Path) -> None:
    """Write contents to a JSON file

    ### Args:
        * data (`Any`): Contents to write. Must be a JSON serializable
        * path (`str | Path`): Path-like object or path as a string of a destination
    """
    async with aiofiles.open(str(path), mode="w", encoding="utf-8") as f:
        await f.write(
            dumps(data, ensure_ascii=False, escape_forward_slashes=False, indent=4)
            if supports_argument(dumps, "escape_forward_slashes")
            else dumps(data, ensure_ascii=False, indent=4)
        )
