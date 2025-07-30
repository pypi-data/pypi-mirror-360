import asyncio
import logging
import pickle
from typing import Any, Literal, cast

from polycrud.connectors.pyredis._utils import _parse_redis_url

from ._base import NULL_VALUE, BaseRedisConnector, T

try:
    from redis.asyncio import Redis, RedisCluster, RedisError
    from redis.asyncio.cluster import ClusterNode
except ImportError as e:
    raise ImportError("Redis package is not installed. Please install it using 'pip install redis'.") from e
_logger = logging.getLogger(__name__)


class AsyncRedisConnector(BaseRedisConnector):
    def __init__(self, redis_url: str, conn_type: Literal["sentinel", "cluster", "standalone"] = "standalone", **kwargs: Any) -> None:
        self.health_check_failures: int = 0
        self.client: Redis | RedisCluster | None = None
        self.redis_url = redis_url
        self.conn_type = conn_type
        self.kwargs = kwargs or {}

    def connect(self) -> None:
        """
        Connect to Redis.
        The redis_url should be in the format:
        - For standalone: redis://username:password@host:port/db
        - For cluster: redis://username:password@host1:port1,host2:port2,host3:port3/db
        - For sentinel: redis-sentinel://username:password@host1:port1,host2:port2,host3:port3/db
        """
        try:
            if self.conn_type == "standalone":
                self.client = Redis.from_url(url=self.redis_url)
            elif self.conn_type == "sentinel":
                raise NotImplementedError("Sentinel connection is not implemented yet.")
            elif self.conn_type == "cluster":
                # Parse the Redis URL to extract host and port
                parsed_url = _parse_redis_url(self.redis_url)
                nodes = [ClusterNode(host, port) for host, port in parsed_url["hosts"]]
                self.client = RedisCluster(
                    startup_nodes=nodes,
                    decode_responses=False,
                    password=parsed_url["password"],
                    username=parsed_url["username"],
                    **self.kwargs,
                )  # type: ignore
        except RedisError as e:
            _logger.error(f"Error connecting to Redis: {e}")
            raise e

    async def close(self) -> None:
        """
        Close the Redis connection.
        """
        if self.client:
            try:
                await self.client.close()
            except RedisError as e:
                _logger.error(f"Error closing Redis connection: {e}")

    async def restart(self) -> None:
        """
        Restart the Redis connection.
        """
        await self.close()
        self.connect()

    async def set_object(self, key: str, value: Any, expire_seconds: int = 0) -> bool:
        if self.client is None:
            return False
        try:
            if expire_seconds == 0:
                await self.client.set(key, self._encode(value))
            else:
                await self.client.setex(key, expire_seconds, self._encode(value))
            return True
        except RedisError as e:
            _logger.error(f"Error setting object in Redis: {e}")
            return False

    async def get_object(self, model_class: type[T] | None, *, key: str) -> T | None | bytes:
        if self.client is None:
            return None

        raw_data = await self.client.get(key)
        try:
            object_data = self._decode(model_class, raw_data) if raw_data else None
            if object_data == NULL_VALUE:
                return NULL_VALUE
            return cast(T, object_data)
        except pickle.PickleError as e:
            _logger.error(f"Error loading object from Redis: {e}")
            return None

    async def delete_key(self, key: str) -> bool:
        if not self.client:
            return False
        try:
            await self.client.delete(key)
            return True
        except RedisError as e:
            _logger.error(f"Error deleting key from Redis: {e}")
            return False

    async def health_check(self) -> bool:
        if self.client is None:
            self.health_check_failures += 1
            _logger.error(f"Redis health check failed: redis is not initialized, failures={self.health_check_failures}")
            return False
        try:
            pong = await self.client.ping()
            if pong:
                self.health_check_failures = 0
                return True
            self.health_check_failures += 1
            _logger.error(f"Redis health check failed: did not receive PONG., failures={self.health_check_failures}")
        except asyncio.CancelledError:
            self.health_check_failures += 1
            _logger.error(f"Redis health check failed: operation was cancelled, failures={self.health_check_failures}")
        except Exception as e:
            self.health_check_failures += 1
            _logger.error(f"Redis health check failed: error={e}, failures={self.health_check_failures}")

        if self.health_check_failures > 20:
            _logger.warning("Redis health check failed 10 times, attempting to restart Redis client.")
            await self.restart()
            self.health_check_failures = 0

        return False
