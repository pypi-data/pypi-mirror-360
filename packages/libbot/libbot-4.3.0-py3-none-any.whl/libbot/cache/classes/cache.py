from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pymemcache
import redis


class Cache(ABC):
    client: pymemcache.Client | redis.Redis

    @classmethod
    @abstractmethod
    def from_config(cls, engine_config: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def get_json(self, key: str) -> Any | None:
        # TODO This method must also carry out ObjectId conversion!
        pass

    @abstractmethod
    def get_string(self, key: str) -> str | None:
        pass

    @abstractmethod
    def get_object(self, key: str) -> Any | None:
        pass

    @abstractmethod
    def set_json(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        # TODO This method must also carry out ObjectId conversion!
        pass

    @abstractmethod
    def set_string(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        pass

    @abstractmethod
    def set_object(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass
