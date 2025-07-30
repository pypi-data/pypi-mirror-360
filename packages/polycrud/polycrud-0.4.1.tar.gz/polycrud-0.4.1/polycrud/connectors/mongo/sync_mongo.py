from __future__ import annotations

import logging
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from contextvars import ContextVar, Token
from datetime import datetime
from enum import Enum
from typing import Any, TypeAlias, TypeVar

from bson import ObjectId

from polycrud import exceptions
from polycrud.cache import cache
from polycrud.connectors.base import DEFAULT_CACHE_TTL, BaseConnector
from polycrud.entity import ModelEntity

try:
    import pymongo
    from pymongo import MongoClient, errors
    from pymongo.client_session import ClientSession
    from pymongo.database import Database
    from pymongo.synchronous.collection import Collection
except ImportError as e:
    raise ImportError("pymongo is required for MongoDB support. Please install it with 'pip install pymongo'") from e

Logger = logging.getLogger(__name__)
_DocumentType: TypeAlias = dict[str, Any]
Transaction: TypeAlias = ClientSession

T = TypeVar("T", bound=ModelEntity)
P = TypeVar("P")


class Sort(Enum):
    DESCENDING = pymongo.DESCENDING
    ASCENDING = pymongo.ASCENDING


_transaction_context: ContextVar[Transaction] = ContextVar("_transaction")


class MongoConnector(BaseConnector):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        auth_source: str,
        **kwargs: Any,
    ) -> None:
        self.db_config = {"host": host, "port": port, "username": username, "password": password, "auth_source": auth_source, **kwargs}
        self.client: MongoClient[_DocumentType] | None = None
        self.db: Database[_DocumentType] | None = None

    def connect(self) -> None:
        """
        Connect to the data source.
        """
        if self.client is None:
            auth_source = self.db_config.pop("auth_source")
            self.client = MongoClient(**self.db_config)
            Logger.info("Connected to MongoDB at %s:%d", self.db_config["host"], self.db_config["port"])

            self.db = self.client.get_database(auth_source)

    def disconnect(self) -> None:
        """
        Disconnect from the data source.
        """
        if self.client:
            self.client.close()
            Logger.info("Disconnected from MongoDB")
            self.client = None

    def create_index(self, collection: type[T], fields: str | tuple[str, ...], unique: bool = True) -> None:
        self._get_collection(collection).create_index(fields, unique=unique)

    @cache()
    def find_one(
        self,
        collection: type[T],
        raise_if_not_found: bool = False,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> T | None:
        result = self._get_collection(collection).find_one(self._to_mongo_dict(kwargs, True), session=_transaction_context.get(None))
        if result is None:
            if raise_if_not_found:
                raise exceptions.NotFoundError(f"Record not found in {collection.__name__} with {kwargs}")
            return result
        doc = self._to_entity_dict(result)
        return collection(**doc)

    @cache()
    def find_many(
        self,
        collection: type[T],
        *,
        limit: int = 10_000,
        offset: int = 0,
        sort_by: str = "_id",
        sort_dir: Sort = Sort.DESCENDING,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> list[T]:
        doc = self._to_mongo_dict(kwargs, True)
        sort = [(sort_by, sort_dir.value)]
        response = self._get_collection(collection).find(doc, sort=sort, limit=limit, skip=offset, session=_transaction_context.get(None))
        entities = [self._to_entity_dict(x) for x in response]
        result = [collection(**x) for x in entities]
        return result

    @cache()
    def update_one(
        self,
        obj: T,
        in_place: bool = True,
        attributes: Iterable[str] = None,
        exclude_fields: Iterable[str] = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> T:
        doc = self._to_mongo_dict(self._model_dump(obj, attributes, exclude_fields), False)
        assert isinstance(obj.id, str)
        if in_place:
            updated_doc = self._get_collection(obj).find_one_and_update(
                {"_id": ObjectId(obj.id)},
                {"$set": doc},
                return_document=pymongo.ReturnDocument.AFTER,
                session=_transaction_context.get(None),
            )
            return obj.__class__(**self._to_entity_dict(updated_doc))
        self.delete_one(type(obj), id=obj.id)
        return self.insert_one(obj)

    @cache()
    def update_many(
        self,
        collection: type[T],
        filter: dict[str, Any],
        updates: dict[str, Any],
        _upsert: bool = False,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> int:
        if not filter:
            raise exceptions.InvalidArgumentError("Filter must be non-empty.")
        if not updates:
            raise exceptions.InvalidArgumentError("Updates must be non-empty.")

        # Convert the filter and updates to MongoDB-compatible formats
        mongo_filter = self._to_mongo_dict(filter, query=True)
        # Handle the case where _id might be a string or list of strings
        if "_id" in mongo_filter:
            if isinstance(mongo_filter["_id"], str):
                # Convert single string _id to ObjectId
                mongo_filter["_id"] = ObjectId(mongo_filter["_id"])
            elif isinstance(mongo_filter["_id"], dict):
                # Check if we have something like {"_id": {"$in": [list_of_str_ids]}}
                if "$in" in mongo_filter["_id"]:
                    mongo_filter["_id"]["$in"] = [ObjectId(str_id) for str_id in mongo_filter["_id"]["$in"]]

        mongo_updates = {"$set": self._to_mongo_dict(updates, query=False)}

        #     Logger.debug("process db.update_many on collection %s", collection.__name__)

        try:
            result = self._get_collection(collection).update_many(
                mongo_filter,
                mongo_updates,
                upsert=_upsert,
                session=_transaction_context.get(None),
            )
            #         Logger.debug("Updated %d documents in collection %s", result.modified_count, collection.__name__)
            return result.modified_count
        except errors.PyMongoError as e:
            Logger.error("Failed to update documents in collection %s: %s", collection.__name__, e)
            raise exceptions.ExternalError(f"Failed to update documents in collection {collection.__name__}") from e

    @cache()
    def insert_one(
        self, obj: T, *, _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL, _override_cache_key: str | None = None
    ) -> T:
        doc = self._to_mongo_dict(self._model_dump(obj), False)
        try:
            # Logger.debug("process db.insert %s", obj.__class__.__name__)
            doc["_id"] = self._get_collection(obj).insert_one(doc, session=_transaction_context.get(None)).inserted_id
            return obj.__class__(**self._to_entity_dict(doc))
        except errors.DuplicateKeyError as e:
            raise exceptions.DuplicateKeyError(f"Duplicate records {obj.__class__.__name__}") from e

    @cache()
    def insert_many(
        self, objs: list[T], *, _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL, _override_cache_key: str | None = None
    ) -> list[T]:
        col = set(type(o) for o in objs)
        if len(col) > 1:
            raise exceptions.InvalidArgumentError("All objects must belong to the same collection")

        typ = list(col)[0]
        docs = [self._to_mongo_dict(self._model_dump(o), False) for o in objs]
        try:
            # Logger.debug("process db.insert list class %s", typ.__class__.__name__)
            insert_result = self._get_collection(typ).insert_many(docs, session=_transaction_context.get(None))
            objs = []
            for doc, id in zip(docs, insert_result.inserted_ids, strict=True):
                doc["_id"] = id
                objs.append(typ(**self._to_entity_dict(doc)))
            return objs
        except errors.DuplicateKeyError as e:
            raise exceptions.DuplicateKeyError("Duplicate records") from e

    @cache()
    def delete_one(
        self,
        collection: type[T],
        *,
        id: str,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> None:
        if not id:
            return

        Logger.debug("process db.delete record %s", collection.__name__)
        doc = self._get_collection(collection).find_one_and_delete({"_id": ObjectId(id)})
        if doc is None:
            raise exceptions.NotFoundError("Error finding record in pymongo")
        doc["collection"] = collection.__name__
        doc["deleted_at"] = datetime.now()

    @cache()
    def delete_many(
        self,
        collection: type[T],
        *,
        ids: list[str],
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> None:
        if not ids:
            return

        txn = _transaction_context.get(None)
        _ids = [ObjectId(x) for x in ids]
        docs = list(self._get_collection(collection).find({"_id": {"$in": _ids}}, session=txn))
        if len(docs) != len(_ids):
            raise exceptions.NotFoundError("Error finding record to delete")
        Logger.debug("process db.delete list %s", collection.__name__)
        deleted_at = datetime.now()
        for doc in docs:
            doc["collection"] = collection.__name__
            doc["deleted_at"] = deleted_at
        self._get_collection(collection).delete_many({"_id": {"$in": _ids}}, session=txn)

    @cache()
    def count(
        self,
        collection: type[T],
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> int:
        return self._get_collection(collection).count_documents(self._to_mongo_dict(kwargs, True), session=_transaction_context.get(None))

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        session: Transaction | None = None
        token: Token[Transaction] | None = None
        try:
            assert self.client is not None
            session = self.client.start_session(causal_consistency=True)
            token = _transaction_context.set(session)
            with session.start_transaction():
                yield
        except Exception as e:
            if session and session.in_transaction:
                session.abort_transaction()
            raise e
        finally:
            if session:
                session.end_session()
            if token:
                _transaction_context.reset(token)

    def health_check(self) -> bool:
        """
        Check the health of the connection.
        """
        assert self.client is not None
        try:
            self.client.server_info()
            return True
        except pymongo.errors.PyMongoError as e:
            Logger.error(f"Error connecting to MongoDB: {e}")
            return False

    def _get_collection(self, target: ModelEntity | type | str) -> Collection[_DocumentType]:
        assert self.db is not None
        if isinstance(target, str):
            return self.db[target]
        if isinstance(target, type):
            return self.db[target.__name__]
        return self.db[type(target).__name__]

    @staticmethod
    def _model_dump(
        obj: T, include: Iterable[str] | None = None, exclude: Iterable[str] | None = None, serialize_as_any: bool = False
    ) -> dict[str, Any]:
        doc = obj.model_dump(
            include=set(include) if include else None, exclude=set(exclude) if exclude else None, serialize_as_any=serialize_as_any
        )
        now = datetime.now()
        if "created_at" in doc and not doc["created_at"]:
            doc["created_at"] = now

        if exclude is None or "modified_at" not in exclude:
            doc["modified_at"] = now
        return doc

    def _to_mongo_dict(self, doc: _DocumentType, query: bool) -> _DocumentType:
        doc = {k: self._to_mongo_value(v, query) for k, v in doc.items()}
        if "id" in doc:
            doc["_id"] = ObjectId(doc.pop("id"))
        return doc

    def _to_mongo_value(self, v: Any, query: bool) -> Any:
        # if isinstance(v, str):
        #     if ObjectId.is_valid(v):
        #         return ObjectId(v)
        #     return ObjectId(v.encode() if v else None)
        if isinstance(v, set | list):
            values = [self._to_mongo_value(x, False) for x in v]
            if query:
                return {"$in": values}
            return values
        return v

    def _to_entity_dict(self, doc: _DocumentType) -> _DocumentType:
        doc = {k: self._to_entity_value(v) for k, v in doc.items()}
        doc["id"] = doc.pop("_id") if "_id" in doc else ""
        return doc

    def _to_entity_value(self, v: Any) -> Any:
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, list):
            return [self._to_entity_value(x) for x in v]
        return v
