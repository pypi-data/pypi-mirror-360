from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from .cache_ops.async_cache import cache, cache_info, cache_is_healthy, flush_cache, setup

if TYPE_CHECKING:
    from polycrud.connectors.pyredis import AsyncRedisConnector

__all__ = ["cache", "cache_is_healthy", "flush_cache", "init_cache", "cache_info"]


@overload
def init_cache(
    *,
    redis_connector: AsyncRedisConnector,
    ttl: int = 3600 * 4,
    prefix: str = "polycrud",
) -> None: ...


@overload
def init_cache(
    *,
    redis_url: str,
    conn_type: Literal["standalone", "cluster"] = "standalone",
    ttl: int = 3600 * 4,
    prefix: str = "polycrud",
) -> None: ...


def init_cache(
    *,
    redis_connector: AsyncRedisConnector | None = None,
    redis_url: str | None = None,
    conn_type: Literal["standalone", "cluster"] = "standalone",
    ttl: int = 3600 * 4,
    prefix: str = "polycrud",
) -> None:
    """
    Initialize the async cache with a Redis connector.

    Args:
        redis_connector (AsyncRedisConnector): The Redis connector instance.
        redis_url (str, optional): The Redis URL. Defaults to None.
        conn_type (Literal["standalone", "cluster"], optional): The type of Redis connection. Defaults to "standalone".
        ttl (int, optional): Time-to-live for cache entries. Defaults to 3600 * 4.
        prefix (str, optional): Prefix for cache keys. Defaults to "polycrud".
    """
    if redis_connector is None and redis_url is None:
        raise ValueError("Either redis_connector or redis_url must be provided.")
    if redis_connector and redis_url:
        raise ValueError("Only one of redis_connector or redis_url should be provided.")
    if redis_connector is None:
        from polycrud.connectors.pyredis import AsyncRedisConnector

        assert redis_url is not None
        redis_connector = AsyncRedisConnector(redis_url=redis_url, conn_type=conn_type)
    setup(redis_connector=redis_connector, ttl=ttl, prefix=prefix)
