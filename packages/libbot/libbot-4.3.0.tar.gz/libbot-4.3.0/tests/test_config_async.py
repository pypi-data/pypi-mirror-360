from pathlib import Path
from typing import Any, List

import pytest
from libbot.utils import config_delete, config_get, config_set


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "args, expected",
    [
        (["locale"], "en"),
        (["bot_token", "bot"], "sample_token"),
    ],
)
async def test_config_get_valid(args: List[str], expected: str, location_config: Path):
    assert await config_get(args[0], *args[1:], config_file=location_config) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "args, expected",
    [
        (["bot_stonks", "bot"], pytest.raises(KeyError)),
    ],
)
async def test_config_get_invalid(args: List[str], expected: Any, location_config: Path):
    with expected:
        assert await config_get(args[0], *args[1:], config_file=location_config) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key, path, value",
    [
        ("locale", [], "en"),
        ("bot_token", ["bot"], "sample_token"),
    ],
)
async def test_config_set(key: str, path: List[str], value: Any, location_config: Path):
    await config_set(key, value, *path, config_file=location_config)
    assert await config_get(key, *path, config_file=location_config) == value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key, path",
    [
        ("bot_token", ["bot"]),
    ],
)
async def test_config_delete(key: str, path: List[str], location_config: Path):
    await config_delete(key, *path, config_file=location_config)
    assert key not in (await config_get(*path, config_file=location_config))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key, path",
    [
        ("bot_lol", ["bot"]),
    ],
)
async def test_config_delete_missing(key: str, path: List[str], location_config: Path):
    assert await config_delete(key, *path, missing_ok=True, config_file=location_config) is None
