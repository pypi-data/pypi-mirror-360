from typing import Dict, Any, Literal, Optional

from ..classes import CacheMemcached, CacheRedis


def create_cache_client(
    config: Dict[str, Any],
    engine: Literal["memcached", "redis"] | None = None,
    prefix: Optional[str] = None,
) -> CacheMemcached | CacheRedis:
    if engine not in ["memcached", "redis"] or engine is None:
        raise KeyError(f"Incorrect cache engine provided. Expected 'memcached' or 'redis', got '{engine}'")

    if "cache" not in config or engine not in config["cache"]:
        raise KeyError(
            f"Cache configuration is invalid. Please check if all keys are set (engine: '{engine}')"
        )

    match engine:
        case "memcached":
            return CacheMemcached.from_config(config["cache"][engine], prefix=prefix)
        case "redis":
            return CacheRedis.from_config(config["cache"][engine], prefix=prefix)
        case _:
            raise KeyError(f"Cache implementation for the engine '{engine}' is not present.")
