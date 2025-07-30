from __future__ import annotations

import enum
import logging
import traceback
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from polycrud import exceptions
from polycrud.constants import NULL_VALUE
from polycrud.entity import ModelEntity

if TYPE_CHECKING:
    from polycrud.connectors.pyredis import AsyncRedisConnector, RedisConnector

_logger = logging.getLogger(__name__)
ModelT = TypeVar("ModelT", bound=ModelEntity)


class CacheStatus(str, enum.Enum):
    Hit = "hit"
    Miss = "miss"
    Skip = "skip"


class BaseRedisCache:
    _metrics: dict[str, Any] = defaultdict(lambda: {CacheStatus.Hit: 0, CacheStatus.Miss: 0, CacheStatus.Skip: 0})

    def __init__(self, ttl: int = 3600 * 4, prefix: str = "polycrud") -> None:
        assert prefix, "Prefix cannot be None"
        self.ttl = ttl
        self.prefix = prefix

    def track(self, fn_name: str, status: Literal[CacheStatus.Hit, CacheStatus.Miss, CacheStatus.Skip]) -> None:
        # status is one of: "hit", "miss", "skip"
        if status in self._metrics[fn_name]:
            self._metrics[fn_name][status] += 1

    def get_metrics(self) -> dict[str, dict[str, int]]:
        return dict(self._metrics)

    def _format_key(self, key: str) -> str:
        return f"{self.prefix}:{key}" if self.prefix else key


class RedisCache(BaseRedisCache):
    def __init__(self, redis_connector: RedisConnector, ttl: int = 3600 * 4, prefix: str = "polycrud") -> None:
        super().__init__(ttl, prefix)
        self.redis_connector = redis_connector
        self.redis_connector.connect()

    def initialize(self) -> None:
        try:
            self.redis_connector.connect()
            if not self.redis_connector.health_check():
                self.redis_connector.connect()
        except Exception as e:
            _logger.error(f"Failed to initialize Redis connection: {str(e)}")
            raise exceptions.RedisConnectionError(f"Could not connect to Redis: {str(e)}") from e

    def get(self, key: str, model_cls: type[ModelT] | None = None) -> ModelT | bytes | None:
        if not self.redis_connector:
            return None
        try:
            if model_cls is None:
                value = self.redis_connector.get_object(None, key=self._format_key(key))
            else:
                value = self.redis_connector.get_object(model_cls, key=self._format_key(key))  # type: ignore
            if value == NULL_VALUE:
                return NULL_VALUE
            return value
        except Exception as e:
            _logger.warning(f"Redis get failed for key={key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int | None = None, tags: list[str] | None = None) -> None:
        if not self.redis_connector.client:
            return
        try:
            full_key = self._format_key(key)
            self.redis_connector.set_object(full_key, value, ttl or self.ttl)
            if tags:
                self._add_tags(full_key, tags)
        except Exception as e:
            traceback.print_exc()
            _logger.warning(f"Redis set failed for key={key}: {e}")

    def clear(self, key: str) -> None:
        if not self.redis_connector.client:
            _logger.warning("Redis clear failed: Redis client is not connected.")
            return
        try:
            self.redis_connector.delete_key(self._format_key(key))
        except Exception as e:
            _logger.warning(f"Redis clear failed for key={key}: {e}")

    def _add_tags(self, key: str, tags: list[str]) -> None:
        if not self.redis_connector.client:
            return
        try:
            pipe = self.redis_connector.client.pipeline()
            for tag in tags:
                pipe.sadd(f"tag:{tag}", key)
            pipe.execute()
        except Exception as e:
            _logger.warning(f"Redis add_tags failed for key={key}: {e}")

    def invalidate_tags(self, tags: list[str]) -> None:
        if not tags or not self.redis_connector.client:
            return
        try:
            pipe = self.redis_connector.client.pipeline()
            all_keys: set[str] = {
                key
                for tag in tags
                for key in self.redis_connector.client.smembers(f"tag:{tag}")  # type: ignore
            }
            if all_keys:
                pipe.delete(*all_keys)
            pipe.delete(*[f"tag:{tag}" for tag in tags])
            pipe.execute()
        except Exception as e:
            _logger.warning(f"Redis invalidate_tags failed: {e}")

    def pop(self, key: str) -> None:
        if not self.redis_connector.client:
            _logger.warning("Redis pop failed: Redis client is not connected.")
            return
        try:
            self.redis_connector.delete_key(self._format_key(key))
        except Exception as e:
            _logger.warning(f"Redis pop failed for key={key}: {e}")

    def invalidate_all(self) -> None:
        if not self.redis_connector.client:
            _logger.warning("Redis invalidate_all failed: Redis client is not connected.")
            return
        try:
            pattern = f"{self.prefix}:*"
            tag_pattern = "tag:*"
            keys_to_delete = set()

            # Use int for cursor as required by redis-py
            cursor = 0
            while True:
                cursor, keys = self.redis_connector.client.scan(cursor=cursor, match=pattern, count=100)  # type: ignore
                keys_to_delete.update(keys)
                if cursor == 0:
                    break

            # Repeat for tag keys
            cursor = 0
            tag_keys = set()
            while True:
                cursor, keys = self.redis_connector.client.scan(cursor=cursor, match=tag_pattern, count=100)  # type: ignore
                tag_keys.update(keys)
                if cursor == 0:
                    break

            all_keys = list(keys_to_delete.union(tag_keys))
            if all_keys:
                self.redis_connector.client.delete(*all_keys)
                _logger.info(f"Redis invalidate_all deleted {len(all_keys)} keys.")
            else:
                _logger.info("Redis invalidate_all: no matching keys found.")
        except Exception as e:
            _logger.warning(f"Redis invalidate_all failed: {e}")


class AsyncRedisCache(BaseRedisCache):
    def __init__(self, redis_connector: AsyncRedisConnector, ttl: int = 3600 * 4, prefix: str = "polycrud") -> None:
        super().__init__(ttl, prefix)
        self.redis_connector = redis_connector
        self.redis_connector.connect()

    async def initialize(self) -> None:
        try:
            self.redis_connector.connect()
            if not await self.redis_connector.health_check():
                self.redis_connector.connect()
        except Exception as e:
            _logger.error(f"Failed to initialize Redis connection: {str(e)}")
            raise exceptions.RedisConnectionError(f"Could not connect to Redis: {str(e)}") from e

    async def get(self, key: str, model_cls: type[ModelT] | None = None) -> ModelT | bytes | None:
        if not self.redis_connector.client:
            _logger.warning("Redis get failed: Redis client is not connected.")
            return None
        try:
            if model_cls is None:
                value = await self.redis_connector.get_object(None, key=self._format_key(key))
            else:
                value = await self.redis_connector.get_object(model_cls, key=self._format_key(key))  # type: ignore
            if value == NULL_VALUE:
                return NULL_VALUE
            return value
        except Exception as e:
            _logger.warning(f"Redis get failed for key={key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None, tags: list[str] | None = None) -> None:
        if not self.redis_connector.client:
            return None
        try:
            full_key = self._format_key(key)
            await self.redis_connector.set_object(full_key, value, ttl or self.ttl)
            if tags:
                await self._add_tags(full_key, tags)
        except Exception as e:
            _logger.warning(f"Redis set failed for key={key}: {e}")

    async def clear(self, key: str) -> None:
        if not self.redis_connector.client:
            _logger.warning("Redis clear failed: Redis client is not connected.")
            return None
        try:
            await self.redis_connector.delete_key(self._format_key(key))
        except Exception as e:
            _logger.warning(f"Redis clear failed for key={key}: {e}")

    async def _add_tags(self, key: str, tags: list[str]) -> None:
        if not self.redis_connector.client:
            _logger.warning("Redis add_tags failed: Redis client is not connected.")
            return
        try:
            pipe = self.redis_connector.client.pipeline()
            for tag in tags:
                await pipe.sadd(f"tag:{tag}", key)  # type: ignore
            await pipe.execute()
        except Exception as e:
            _logger.warning(f"Redis add_tags failed for key={key}: {e}")

    async def invalidate_tags(self, tags: list[str]) -> None:
        if not tags or not self.redis_connector.client:
            _logger.warning("Redis invalidate_tags failed: Redis client is not connected.")
            return None
        try:
            pipe = self.redis_connector.client.pipeline()
            all_keys = set()
            for tag in tags:
                keys = await self.redis_connector.client.smembers(f"tag:{tag}")  # type: ignore
                all_keys.update(keys)

            if all_keys:
                await pipe.delete(*all_keys)

            # Delete the tag sets themselves
            for tag in tags:
                await pipe.delete(f"tag:{tag}")

            await pipe.execute()
        except Exception as e:
            _logger.warning(f"Redis invalidate_tags failed: {e}")

    async def pop(self, key: str) -> None:
        if not self.redis_connector.client:
            _logger.warning("Redis pop failed: Redis client is not connected.")
            return None
        try:
            await self.redis_connector.delete_key(self._format_key(key))
        except Exception as e:
            _logger.warning(f"Redis pop failed for key={key}: {e}")

    async def invalidate_all(self) -> None:
        if not self.redis_connector.client:
            _logger.warning("Redis invalidate_all failed: Redis client is not connected.")
            return
        try:
            cache_pattern = f"{self.prefix}:*"
            tag_pattern = "tag:*"
            keys_to_delete = set()

            # Scan all cache keys with prefix
            cursor: int = 0
            while True:
                cursor, keys = await self.redis_connector.client.scan(cursor=cursor, match=cache_pattern, count=100)
                keys_to_delete.update(keys)
                if cursor == 0:
                    break

            # Scan all tag keys
            cursor = 0
            while True:
                cursor, tag_keys = await self.redis_connector.client.scan(cursor=cursor, match=tag_pattern, count=100)
                keys_to_delete.update(tag_keys)
                if cursor == 0:
                    break

            if keys_to_delete:
                await self.redis_connector.client.delete(*keys_to_delete)
                _logger.info(f"Redis invalidate_all deleted {len(keys_to_delete)} keys.")
            else:
                _logger.info("Redis invalidate_all: no matching keys found.")
        except Exception as e:
            _logger.warning(f"Redis invalidate_all failed: {e}")
