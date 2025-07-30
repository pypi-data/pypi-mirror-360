from pathlib import Path

from libbot.cache.classes import Cache
from libbot.cache.manager import create_cache_client

try:
    from ujson import JSONDecodeError, dumps, loads
except ImportError:
    from json import JSONDecodeError, dumps, loads

from typing import Any, Dict

import pytest


@pytest.mark.parametrize(
    "engine",
    [
        "memcached",
        "redis",
    ],
)
def test_cache_creation(engine: str, location_config: Path):
    with open(location_config, "r", encoding="utf-8") as file:
        config: Dict[str, Any] = loads(file.read())

    cache: Cache = create_cache_client(config, engine)
    assert isinstance(cache, Cache)
