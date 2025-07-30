from enum import Enum
from typing import Any

from polycrud.utils import helper

_CACHED_NONE_MARKER = {"__cached_none__": True}


class QueryType(str, Enum):
    FindOne = "find_one"
    FindMany = "find_many"
    FullTextSearch = "full_text_search"
    SemanticSearch = "semantic_search"
    Aggregate = "aggregate"
    RawQuery = "raw_query"
    InsertOne = "insert_one"
    InsertMany = "insert_many"
    UpdateOne = "update_one"
    DeleteOne = "delete_one"
    DeleteMany = "delete_many"


def get_query_type(fn_name: str) -> QueryType | None:
    return next((qt for qt in QueryType if qt in fn_name), None)


def get_tags(base: str, collection: str, obj_id: Any = None) -> list[str]:
    tags = [base, f"{base}:{collection}"]
    if obj_id is not None:
        tags.append(f"{base}:{collection}:{obj_id}")
    return tags


def get_model_class_from_args(args: tuple[Any, ...], kwargs: dict[str, Any]) -> type | None:
    """Extract model class from arguments."""
    from polycrud.entity import ModelEntity

    # Check args first
    if len(args) > 1:
        if isinstance(args[1], type):
            return args[1]
        if isinstance(args[1], ModelEntity):
            return args[1].__class__
        if isinstance(args[1], list) and args[1] and isinstance(args[1][0], ModelEntity):
            return args[1][0].__class__

    # Then check kwargs
    if "collection" in kwargs and isinstance(kwargs["collection"], type):
        return kwargs["collection"]
    if "obj" in kwargs and kwargs["obj"] is not None:
        return kwargs["obj"].__class__  # type: ignore
    if "objs" in kwargs and kwargs["objs"] and len(kwargs["objs"]) > 0:
        return kwargs["objs"][0].__class__  # type: ignore

    return None


def build_cache_key(
    cls_name: str, model_name: str, fn_name: str, args: tuple[Any, ...], kwargs: dict[str, Any], key_hash: str | None = None
) -> str:
    """Build a consistent cache key."""
    # If a key_hash is provided, use it
    cloned_kwargs = kwargs.copy()
    if key_hash:
        return f"{cls_name}:{model_name}:{fn_name}:{key_hash}"
    if fn_name == QueryType.RawQuery:
        copy_args = args[1:] if len(args) > 1 else []
        valid_params = [arg for arg in copy_args if helper.is_json_serializable(arg)]
        cloned_kwargs.update({"args": valid_params})

    key_hash = helper.deep_container_fingerprint([cls_name, model_name, cloned_kwargs])
    return f"{cls_name}:{model_name}:{fn_name}:{key_hash}"
