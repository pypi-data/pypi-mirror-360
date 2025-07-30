import pickle
from typing import Any, TypeVar

import orjson
from pydantic import BaseModel

T = TypeVar("T")

NULL_VALUE = b"null"  # Optional: use orjson.dumps(None) instead for compatibility
AUTO_TYPE = "auto"


def is_type_any(tp: type) -> bool:
    return tp is Any  # type: ignore


class BaseRedisConnector:
    """
    Base class for Redis connectors.
    """

    @staticmethod
    def _encode(value: Any) -> bytes:
        """
        Efficiently encode a Python object for Redis storage.
        Uses orjson if possible, falls back to pickle. Simple types are UTF-8 encoded.
        """
        if value is None:
            return b"null"  # Optional: use orjson.dumps(None) instead for compatibility

        if isinstance(value, bytes | bytearray):
            return bytes(value)

        if isinstance(value, str | int | float | bool):
            return str(value).encode("utf-8")

        if isinstance(value, BaseModel):
            try:
                return orjson.dumps(value.model_dump())  # pylint: disable=E1101
            except Exception:
                pass  # Fallback to pickle below

        if isinstance(value, list | dict | tuple):
            try:
                return orjson.dumps(value)  # pylint: disable=E1101
            except Exception:
                pass

        # Fallback to pickle
        return b"p" + pickle.dumps(value, protocol=5)

    @staticmethod
    def _decode(model_class: type[T] | None, value: bytes) -> Any:
        """
        Safely decode Redis bytes back to Python object.
        Tries JSON deserialization first; falls back to UTF-8 string.
        """
        if not value:  # Handles None or b''
            return None if value is None else ""

        if value == NULL_VALUE:
            return NULL_VALUE

        if value.startswith(b"p"):
            try:
                return pickle.loads(value[1:])
            except Exception as e:
                raise ValueError(f"Unable to decode pickled value: {e}") from e

        try:
            result = orjson.loads(value)  # pylint: disable=E1101
            if result is None:
                return None
            # if model_class and is_type_any(model_class):
            #     return result
            if model_class and issubclass(model_class, BaseModel):
                return model_class(**result)
            if model_class and issubclass(model_class, tuple):
                return model_class(result)
            return result
        except orjson.JSONDecodeError:  # pylint: disable=E1101
            pass

        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value  # Return raw bytes as last resort
