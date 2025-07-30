import logging
import pickle
from typing import Any, Literal, cast

from polycrud.connectors.pyredis._utils import _parse_redis_url

from ._base import NULL_VALUE, BaseRedisConnector, T

try:
    import redis
    from redis import Redis, RedisError
    from redis.cluster import ClusterNode, RedisCluster
except ImportError as e:
    raise ImportError("Redis package is not installed. Please install it using 'pip install redis'.") from e

_logger = logging.getLogger(__name__)


class RedisConnector(BaseRedisConnector):
    def __init__(self, redis_url: str, conn_type: Literal["sentinel", "cluster", "standalone"] = "standalone") -> None:
        self.health_check_failures: int = 0
        self.client: Redis | RedisCluster | None = None
        self.redis_url = redis_url
        self.conn_type = conn_type

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
                self.client = redis.from_url(url=self.redis_url)
            elif self.conn_type == "sentinel":
                raise NotImplementedError("Sentinel connection is not implemented yet.")
            elif self.conn_type == "cluster":
                # Parse the Redis URL to extract host and port
                parsed_url = _parse_redis_url(self.redis_url)
                nodes = [ClusterNode(host, port) for host, port in parsed_url["hosts"]]
                self.client = RedisCluster(  # type: ignore
                    startup_nodes=nodes, decode_responses=False, password=parsed_url["password"], username=parsed_url["username"]
                )
            else:
                raise ValueError(f"Invalid connection type: {self.conn_type}")
        except RedisError as e:
            _logger.error(f"Error connecting to Redis: {e}")
            raise e

    def close(self) -> None:
        """
        Close the Redis connection.
        """
        if self.client:
            try:
                self.client.close()
            except RedisError as e:
                _logger.error(f"Error closing Redis connection: {e}")

    def restart(self) -> None:
        """
        Restart the Redis connection.
        """
        self.close()
        self.connect()

    def set_object(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """
        Store an object in Redis with optional expiration time.
        """
        if self.client is None:
            return False
        try:
            if expire_seconds == 0:
                self.client.set(key, self._encode(value))
            else:
                self.client.setex(key, expire_seconds, self._encode(value))
            return True
        except RedisError as e:
            _logger.error(f"Error setting object in Redis: {e}")
            return False

    def get_object(self, model_class: type[T] | None, *, key: str) -> T | bytes | None:
        """
        Retrieve and deserialize an object from Redis.
        """
        if self.client is None:
            return None

        raw_data = self.client.get(key)
        try:
            object_data = self._decode(model_class, raw_data) if raw_data else None  # type: ignore
            if object_data == NULL_VALUE:
                return NULL_VALUE

            return cast(T, object_data)
        except pickle.PickleError as e:
            _logger.error(f"Error loading object from Redis: {e}")
            return None

    def delete_key(self, key: str) -> bool:
        """
        Delete a key from Redis.
        """
        if not self.client:
            return False
        try:
            self.client.delete(key)
            return True
        except RedisError as e:
            _logger.error(f"Error deleting key from Redis: {e}")
            return False

    def health_check(self) -> bool:
        """
        Check if Redis connection is healthy.
        """
        if self.client is None:
            self.health_check_failures += 1
            _logger.error(f"Redis health check failed: redis is not initialized, failures={self.health_check_failures}")
            return False

        try:
            pong = self.client.ping()
            if pong:
                self.health_check_failures = 0
                return True
            self.health_check_failures += 1
            _logger.error(f"Redis health check failed: did not receive PONG., failures={self.health_check_failures}")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            self.health_check_failures += 1
            _logger.error(f"Redis health check failed: error={e}, failures={self.health_check_failures}")
        except Exception as e:
            self.health_check_failures += 1
            _logger.error(f"Redis health check failed: error={e}, failures={self.health_check_failures}")

        if self.health_check_failures > 20:
            _logger.warning("Redis health check failed 20 times, attempting to restart Redis client.")
            self.restart()
            self.health_check_failures = 0

        return False
