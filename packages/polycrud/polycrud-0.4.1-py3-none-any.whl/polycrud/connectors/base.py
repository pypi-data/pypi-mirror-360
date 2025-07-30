from collections.abc import Iterable
from typing import Any, Literal, TypeVar

from polycrud.entity import ModelEntity

T = TypeVar("T", bound=ModelEntity)

DEFAULT_CACHE_TTL = 3600 * 4  # 4 hours


class BaseConnector:
    def connect(self, **kwargs: Any) -> None:
        """
        Connect to the data source.
        """
        raise NotImplementedError("Connect method not implemented.")

    def disconnect(self) -> None:
        """
        Disconnect from the data source.
        """
        raise NotImplementedError("Disconnect method not implemented.")

    def health_check(self) -> bool:
        """
        Check the health of the connection.
        """
        raise NotImplementedError("Health check method not implemented.")

    def insert_one(self, obj: T, *, _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL) -> T:
        """
        Insert a single object into the data source.
        """
        raise NotImplementedError("Insert one method not implemented.")

    def insert_many(self, objs: list[T], *, _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL) -> list[T]:
        """
        Insert multiple objects into the data source.
        """
        raise NotImplementedError("Insert many method not implemented.")

    def update_one(
        self, obj: T, *, _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL, _override_cache_key: str | None = None
    ) -> T:
        """
        Update a single object in the data source.
        """
        raise NotImplementedError("Update one method not implemented.")

    def find_one(
        self,
        collection: type[T],
        *,
        query: str | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        raise_if_not_found: bool = False,
        **kwargs: Any,
    ) -> T:
        """
        Find a single object in the data source.
        """
        raise NotImplementedError("Find one method not implemented.")

    def find_many(
        self,
        collection: type[T],
        *,
        limit: int = 10_000,
        offset: int = 0,
        sort_field: str = "id",
        sort_dir: Literal["asc", "desc"] = "asc",
        query: str | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> list[T]:
        """
        Find multiple objects in the data source.
        """
        raise NotImplementedError("Find many method not implemented.")

    def delete_one(
        self,
        collection: type[T],
        *,
        id: int | str,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> Any:
        """
        Delete a single object from the data source.
        """
        raise NotImplementedError("Delete one method not implemented.")

    def delete_many(
        self,
        collection: type[T],
        *,
        ids: list[str | int],
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> list[T]:
        """
        Delete multiple objects from the data source.
        """
        raise NotImplementedError("Delete many method not implemented.")

    def count(
        self,
        collection: type[T],
        *,
        query: str | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> int:
        """
        Count the number of objects in the data source.
        """
        raise NotImplementedError("Count method not implemented.")


class AsyncBaseConnector:
    """
    Base class for asynchronous connectors.
    """

    # def __init__(self, redis_connector: AsyncRedisConnector | None = None, ttl: int = 3600 * 4, cache_prefix: None | str = None):
    #     self.redis_cache_connector: RedisConnector
    #     if redis_connector:
    #         cache.a_setup(redis_connector=redis_connector, ttl=ttl, prefix=cache_prefix)

    async def connect(self, **kwargs: Any) -> None:
        """
        Connect to the data source.
        """
        raise NotImplementedError("Connect method not implemented.")

    async def disconnect(self) -> None:
        """
        Disconnect from the data source.
        """
        raise NotImplementedError("Disconnect method not implemented.")

    async def health_check(self) -> bool:
        """
        Check the health of the connection.
        """
        raise NotImplementedError("Health check method not implemented.")

    async def insert_one(
        self,
        obj: T,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> T:
        """
        Insert a single object into the data source.
        """
        raise NotImplementedError("Insert one method not implemented.")

    async def insert_many(
        self, objs: list[T], _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL, _override_cache_key: str | None = None
    ) -> list[T]:
        """
        Insert multiple objects into the data source.
        """
        raise NotImplementedError("Insert many method not implemented.")

    async def update_one(
        self,
        obj: T,
        attributes: Iterable[str] = None,
        exclude_fields: Iterable[str] = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> T:
        raise NotImplementedError("Update one method not implemented.")

    async def find_one(
        self,
        collection: type[T],
        *,
        query: str | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> T:
        """
        Find a single object in the data source.
        """
        raise NotImplementedError("Find one method not implemented.")

    async def find_many(
        self,
        collection: type[T],
        *,
        limit: int = 10_000,
        offset: int = 0,
        sort_field: str = "id",
        sort_dir: Literal["asc", "desc"] = "asc",
        query: str | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> list[T]:
        """
        Find multiple objects in the data source.
        """
        raise NotImplementedError("Find many method not implemented.")

    async def delete_one(
        self,
        collection: type[T],
        *,
        id: int | str,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> Any:
        """
        Delete a single object from the data source.
        """
        raise NotImplementedError("Delete one method not implemented.")

    async def delete_many(
        self,
        collection: type[T],
        *,
        ids: list[str | int],
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> list[T]:
        """
        Delete multiple objects from the data source.
        """
        raise NotImplementedError("Delete many method not implemented.")

    async def count(
        self,
        collection: type[T],
        query: str | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> int:
        """
        Count the number of objects in the data source.
        Returns:

        """
        raise NotImplementedError("Count method not implemented.")
