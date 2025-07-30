from __future__ import annotations

import logging
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from polycrud.constants import NULL_VALUE
from polycrud.entity import ModelEntity

from ._base import CacheStatus, RedisCache
from ._utils import QueryType, build_cache_key, get_model_class_from_args, get_query_type, get_tags

if TYPE_CHECKING:
    from polycrud.connectors.pyredis import RedisConnector
F = TypeVar("F", bound=Callable[..., Any])

_logger = logging.getLogger(__name__)
ModelT = TypeVar("ModelT", bound=ModelEntity)


class _Settings:
    redis_cache: RedisCache | None = None
    is_ready: bool = False


def setup(redis_connector: RedisConnector, ttl: int = 3600 * 4, prefix: str = "polycrud") -> None:
    if _Settings.redis_cache is not None:
        raise RuntimeError("Redis cache is already set up.")
    _Settings.redis_cache = RedisCache(redis_connector=redis_connector, ttl=ttl, prefix=prefix)
    _Settings.is_ready = True


def cache() -> Callable[[F], F]:
    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not _Settings.is_ready:
                if _Settings.redis_cache is not None:
                    _track(fn.__name__, CacheStatus.Skip)
                    _logger.debug(f"Redis cache is not ready, skipping cache for {fn.__name__}")
                return fn(*args, **kwargs)

            # If no cache is set up, just call the function
            _use_cache = kwargs.pop("_use_cache") if "_use_cache" in kwargs else True
            if _Settings.redis_cache is None or not _use_cache:
                return fn(*args, **kwargs)

            # Determine the class name and model class from the arguments
            fn_name = fn.__name__
            cls_name = args[0].__class__.__name__
            ttl = kwargs.get("_cache_ttl", None)

            try:
                model_class = get_model_class_from_args(args, kwargs)
                model_name = model_class.__name__ if model_class is not None else "Any"
            except Exception:
                # If we can't determine the model class, just call the function
                _track(fn_name, CacheStatus.Skip)
                _logger.debug(f"Could not determine model class for {cls_name}.{fn_name}, skipping cache")
                return fn(*args, **kwargs)

            query_type = get_query_type(fn_name)
            redis_cache = _Settings.redis_cache

            # Get or create the cache key
            _override_cache_key = kwargs.pop("_override_cache_key", None)
            cache_key = build_cache_key(cls_name, model_name, fn_name, args, kwargs, key_hash=_override_cache_key)

            # Handle mutation operations
            if query_type in {
                QueryType.DeleteOne,
                QueryType.UpdateOne,
                QueryType.DeleteMany,
                QueryType.InsertMany,
                QueryType.InsertOne,
            }:
                obj_ids = []

                if query_type == QueryType.DeleteOne:
                    obj_ids = [kwargs.get("id")]
                elif query_type == QueryType.UpdateOne:
                    obj = kwargs.get("obj") or args[1]
                    obj_ids = [getattr(obj, "id", None)]
                elif query_type == QueryType.DeleteMany:
                    obj_ids = kwargs.get("ids", [])

                tags = get_tags(cls_name, model_name)
                tags += [f"{cls_name}:{model_name}:{oid}" for oid in obj_ids if oid]
                redis_cache.invalidate_tags(tags)

                return fn(*args, **kwargs)

            # Handle read operations
            cached = redis_cache.get(cache_key, model_class)
            if cached is not None or cached == NULL_VALUE:
                _track(fn_name, CacheStatus.Hit)
                _logger.debug(f"Cache hit: {cache_key}")
                if cached == NULL_VALUE:
                    # If the cached value is NULL_VALUE, return None
                    return None
                return cached

            # Cache miss, call the function
            _track(fn_name, CacheStatus.Miss)
            _logger.debug(f"Cache miss: {cache_key}")
            result = fn(*args, **kwargs)

            # Determine tags based on query type
            if result is None:
                tags = [f"{cls_name}:{model_name}"]
            else:
                tags = {
                    QueryType.FindOne: [f"{cls_name}:{model_name}:{getattr(result, 'id', '')}"],
                    QueryType.FindMany: [f"{cls_name}:{model_name}"],
                }.get(query_type, [cls_name])  # type: ignore

            redis_cache.set(cache_key, result, ttl=ttl, tags=tags)
            return result

        return cast(F, wrapper)

    return decorator


def cache_is_healthy() -> bool:
    """Check if the Redis cache is healthy."""
    if not _Settings.redis_cache:
        return False
    if _Settings.redis_cache.redis_connector.health_check():
        _Settings.is_ready = True
    else:
        _Settings.is_ready = False
    return _Settings.is_ready


def flush_cache() -> None:
    """Flush the Redis cache."""
    if _Settings.redis_cache:
        _Settings.redis_cache.invalidate_all()
        _logger.info("Redis cache flushed.")
    else:
        _logger.warning("Redis cache is not set up.")


def cache_info() -> dict[str, Any]:
    """
    Get cache information. Print cache status including: misses, hits, skips and cache size. for each function name
    Returns:

    """
    if not _Settings.redis_cache:
        raise RuntimeError("Redis cache is not set up.")
    metrics = _Settings.redis_cache.get_metrics()
    return metrics


def _track(fn_name: str, status: Literal[CacheStatus.Hit, CacheStatus.Miss, CacheStatus.Skip]) -> None:
    if not _Settings.redis_cache:
        raise RuntimeError("Redis cache is not set up.")
    _Settings.redis_cache.track(fn_name, status)
