import logging
from collections.abc import Iterable
from typing import Any, Literal, TypeAlias, cast

from polycrud import acache
from polycrud.connectors.base import DEFAULT_CACHE_TTL, AsyncBaseConnector, T
from polycrud.entity import ModelEntity

try:
    from opensearchpy import AsyncOpenSearch
    from opensearchpy.helpers import async_bulk
except ImportError as e:
    raise ImportError("OpenSearch package is not installed. Please install it using 'pip install opensearch-py'.") from e
_DocumentType: TypeAlias = dict[str, Any]

_logger = logging.getLogger(__name__)


class AsyncOpensearchConnector(AsyncBaseConnector):
    def __init__(self, host: str, port: int, username: str, password: str):
        self.client: AsyncOpenSearch | None = None
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    async def connect(self) -> None:
        self.client = AsyncOpenSearch(hosts=[f"{self.host}:{self.port}"], http_auth=(self.username, self.password))

    async def disconnect(self) -> None:
        if self.client:
            await self.client.close()
            self.client = None

    async def health_check(self) -> bool:
        if not self.client:
            raise RuntimeError("OpenSearch client is not connected.")
        return cast(bool, await self.client.ping())

    async def list_indexes(self) -> list[str]:
        if not self.client:
            raise RuntimeError("OpenSearch client is not connected.")

        response = await self.client.cat.indices(format="json")  # pylint: disable=E1123
        return [index["index"] for index in response]

    @acache.cache()
    async def count(
        self,
        collection: type[T],
        query: str | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        **kwargs: Any,
    ) -> int:
        if not self.client:
            raise RuntimeError("OpenSearch client is not connected.")

        index = self.__get_db_index(collection)

        # Build query DSL
        must_conditions = []

        if query:
            must_conditions.append({"query_string": {"query": query}})

        for field, value in kwargs.items():
            must_conditions.append({"term": {field: value}})

        search_body = {
            "query": {"bool": {"must": must_conditions}},
            "size": 0,  # We only want the count, not the actual documents
        }

        response = await self.client.search(index=index, body=search_body)
        return cast(int, response.get("hits", {}).get("total", {}).get("value", 0))

    @acache.cache()
    async def insert_one(
        self, obj: T, _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL, _override_cache_key: str | None = None
    ) -> T:
        if not self.client:
            raise RuntimeError("OpenSearch client is not connected.")
        data = await self.client.index(  # pylint: disable=E1123
            index=self.__get_db_index(obj),
            id=obj.id,
            body=obj.model_dump(),
            refresh=True,  # Ensure the document is immediately searchable
        )
        if not obj.id:
            obj.id = data["_id"]
        return obj

    @acache.cache()
    async def find_one(
        self,
        collection: type[T],
        *,
        query: str | None = None,
        raise_if_not_found: bool = False,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> T | None:
        if not self.client:
            raise RuntimeError("OpenSearch client is not connected.")

        index = self.__get_db_index(collection)

        # Build query DSL
        must_conditions = []

        if query:
            must_conditions.append({"query_string": {"query": query}})

        for field, value in kwargs.items():
            must_conditions.append({"term": {field: value}})

        search_body = {"query": {"bool": {"must": must_conditions}}, "size": 1}

        response = await self.client.search(index=index, body=search_body)

        hits = response.get("hits", {}).get("hits", [])
        if not hits:
            if raise_if_not_found:
                raise ValueError(f"Document not found for query: {query} with filters: {kwargs}")
            return None

        document = hits[0]["_source"]
        document["id"] = hits[0]["_id"]  # Ensure `id` is included

        return collection(**document)

    @acache.cache()
    async def find_many(
        self,
        collection: type[T],
        *,
        limit: int = 10_000,
        offset: int = 0,
        sort_field: Literal["_id", "_score"] = "_id",
        sort_dir: Literal["asc", "desc"] = "asc",
        query: str | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> list[T]:
        if not self.client:
            raise RuntimeError("OpenSearch client is not connected.")

        index = self.__get_db_index(collection)

        must_conditions = []

        if query:
            must_conditions.append({"query_string": {"query": query}})

        for field, value in kwargs.items():
            must_conditions.append({"term": {field: value}})

        search_body = {
            "query": {"bool": {"must": must_conditions}},
            "from": offset,
            "size": limit,
            "sort": [{sort_field: {"order": sort_dir}}],
        }

        response = await self.client.search(index=index, body=search_body)
        hits = response.get("hits", {}).get("hits", [])

        results = []
        for hit in hits:
            doc = hit["_source"]
            doc["id"] = hit["_id"]
            results.append(collection(**doc))

        return results

    @acache.cache()
    async def full_text_search(
        self,
        collection: type[T],
        query_text: str,
        fields: list[str] | None = None,
        limit: int = 10_000,
        offset: int = 0,
        sort_field: Literal["_id", "_score"] = "_score",
        sort_dir: Literal["asc", "desc"] = "desc",
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> list[T]:
        if not self.client:
            raise RuntimeError("OpenSearch client is not connected.")

        index = self.__get_db_index(collection)

        search_body = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "type": "best_fields",  # You can also use "phrase_prefix", "most_fields", etc.
                    "fields": fields or ["*"],  # Or specify fields like ["title", "description"]
                }
            },
            "from": offset,
            "size": limit,
            "sort": [{sort_field: {"order": sort_dir}}],
        }

        response = await self.client.search(index=index, body=search_body)
        hits = response.get("hits", {}).get("hits", [])

        results = []
        for hit in hits:
            doc = hit["_source"]
            doc["id"] = hit["_id"]
            results.append(collection(**doc))

        return results

    @acache.cache()
    async def semantic_search(
        self,
        collection: type[T],
        query_vector: list[float],
        top_k: int = 10,
        normalize: bool = True,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **filters: Any,
    ) -> list[T]:
        if not self.client:
            raise RuntimeError("OpenSearch client is not connected.")

        index = self.__get_db_index(collection)

        def _normalize_vector(vec: list[float]) -> list[float]:
            norm = sum(x**2 for x in vec) ** 0.5
            return [x / norm for x in vec] if norm else vec

        if normalize:
            query_vector = _normalize_vector(query_vector)

        # Optional keyword filters
        filter_clauses = [{"term": {key: value}} for key, value in filters.items()]

        query_body = {
            "size": top_k,
            "query": {
                "bool": {
                    "filter": filter_clauses,
                    "must": {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                "params": {"query_vector": query_vector},
                            },
                        }
                    },
                }
            },
        }

        response = await self.client.search(index=index, body=query_body)
        hits = response.get("hits", {}).get("hits", [])

        results = []
        for hit in hits:
            doc = hit["_source"]
            doc["id"] = hit["_id"]
            results.append(collection(**doc))

        return results

    @acache.cache()
    async def insert_many(
        self, objs: list[T], _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL, _override_cache_key: str | None = None
    ) -> list[T]:
        try:
            # Prepare bulk actions
            actions = [{"_op_type": "index", "_index": self.__get_db_index(obj), "_source": obj.model_dump()} for obj in objs]

            # Execute bulk operation
            _, failed = await async_bulk(
                client=self.client,
                actions=actions,
                refresh=True,  # Ensure the documents are immediately searchable
            )

            if failed:
                logging.error(f"Some documents failed to be created: {failed}")
                # You might want to handle partial failures differently

            return objs

        except Exception as e:
            logging.error(f"Error creating documents in bulk: {e}")
            return []

    @acache.cache()
    async def update_one(
        self,
        obj: T,
        attributes: Iterable[str] = None,
        exclude_fields: Iterable[str] = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> dict[str, Any] | None:
        if not self.client:
            raise RuntimeError("OpenSearch client is not connected.")
        try:
            response = await self.client.update(  # pylint: disable=E1123
                index=self.__get_db_index(obj),
                id=obj.id,
                body={"doc": obj.model_dump(include=attributes, exclude=exclude_fields)},  # type: ignore
                refresh=True,  # Ensure the document is immediately searchable
            )
            return cast(dict[str, Any], response)
        except Exception as e:
            logging.error(f"Error updating document: {e}")
            return None

    @acache.cache()
    async def delete_one(
        self,
        collection: type[T],
        *,
        id: str | int,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> dict[str, Any] | None:
        if not self.client:
            raise RuntimeError("OpenSearch client is not connected.")
        try:
            response = await self.client.delete(
                index=self.__get_db_index(collection),
                id=id,
            )
            return cast(dict[str, Any], response)
        except Exception as e:
            logging.error(f"Error deleting document: {e}")
            return None

    @acache.cache()
    async def delete_many(
        self,
        collection: type[T],
        *,
        ids: list[str | int],
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> list[dict[str, Any]]:
        # Prepare bulk actions
        actions = [{"_op_type": "delete", "_index": self.__get_db_index(collection), "_id": str(id)} for id in ids]
        try:
            # Execute bulk operation
            data, failed = await async_bulk(
                client=self.client,
                actions=actions,
                refresh=True,  # Ensure the documents are immediately searchable
            )

            if failed:
                logging.error(f"Some documents failed to be deleted: {failed}")
                # You might want to handle partial failures differently

            return cast(list[dict[str, Any]], data)

        except Exception as e:
            logging.error(f"Error deleting documents in bulk: {e}")
            return []

    @staticmethod
    def __get_db_index(target: ModelEntity | type | str) -> str:
        if isinstance(target, type):
            return target.__name__.lower()
        if isinstance(target, str):
            return target
        return target.__class__.__name__.lower()
