try:
    from ujson import JSONDecodeError, dumps
except ImportError:
    from json import dumps, JSONDecodeError

from pathlib import Path
from typing import Any

import pytest
from libbot.utils import json_read, json_write


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path, expected",
    [
        (
            "tests/data/test.json",
            {
                "foo": "bar",
                "abcdefg": ["higklmnop", {"lol": {"kek": [1.0000035, 0.2542, 1337]}}],
            },
        ),
        ("tests/data/empty.json", {}),
    ],
)
async def test_json_read_valid(path: str | Path, expected: Any):
    assert await json_read(path) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path, expected",
    [
        ("tests/data/invalid.json", JSONDecodeError),
        ("tests/data/nonexistent.json", FileNotFoundError),
    ],
)
async def test_json_read_invalid(path: str | Path, expected: Any):
    with pytest.raises(expected):
        await json_read(path)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data, path",
    [
        (
            {
                "foo": "bar",
                "abcdefg": ["higklmnop", {"lol": {"kek": [1.0000035, 0.2542, 1337]}}],
            },
            "tests/data/test.json",
        ),
        ({}, "tests/data/empty.json"),
    ],
)
async def test_json_write(data: Any, path: str | Path):
    await json_write(data, path)

    assert Path(path).is_file()
    with open(path, "r", encoding="utf-8") as f:
        assert f.read() == dumps(data, ensure_ascii=False, indent=4)
