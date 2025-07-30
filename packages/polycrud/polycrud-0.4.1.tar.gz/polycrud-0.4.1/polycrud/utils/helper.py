import json
from hashlib import md5
from typing import Any

DEFAULT_ENCODING = "utf-8"


def json_serializable(obj: dict[str, Any]) -> str | None:
    try:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, OverflowError):
        return None


def is_json_serializable(obj: Any) -> bool:
    return json_serializable(obj) is not None


def deep_container_fingerprint(obj: list[Any] | dict[Any, Any] | Any, encoding: str = DEFAULT_ENCODING) -> str:
    """Calculate a hash which is stable, independent of a containers key order.

    Works for lists and dictionaries. For keys and values, we recursively call
    `hash(...)` on them. Keep in mind that a list with keys in a different order
    will create the same hash!

    Args:
        obj: dictionary or list to be hashed.
        encoding: encoding used for dumping objects as strings

    Returns:
        hash of the container.
    """
    if isinstance(obj, dict):
        return __get_dictionary_fingerprint(obj, encoding)
    if isinstance(obj, list):
        return __get_list_fingerprint(obj, encoding)
    if hasattr(obj, "fingerprint") and callable(obj.fingerprint):
        return obj.fingerprint()  # type: ignore
    return __get_text_hash(str(obj), encoding)


def __get_dictionary_fingerprint(dictionary: dict[Any, Any], encoding: str = DEFAULT_ENCODING) -> str:
    """Calculate the fingerprint for a dictionary.

    The dictionary can contain any keys and values which are either a dict,
    a list or a elements which can be dumped as a string.

    Args:
        dictionary: dictionary to be hashed
        encoding: encoding used for dumping objects as strings

    Returns:
        The hash of the dictionary
    """
    stringified = json.dumps(
        {deep_container_fingerprint(k, encoding): deep_container_fingerprint(v, encoding) for k, v in dictionary.items()},
        sort_keys=True,
    )
    return __get_text_hash(stringified, encoding)


def __get_list_fingerprint(elements: list[Any], encoding: str = DEFAULT_ENCODING) -> str:
    """Calculate a fingerprint for an unordered list.

    Args:
        elements: unordered list
        encoding: encoding used for dumping objects as strings

    Returns:
        the fingerprint of the list
    """
    stringified = json.dumps([deep_container_fingerprint(element, encoding) for element in elements])
    return __get_text_hash(stringified, encoding)


def __get_text_hash(text: str, encoding: str = DEFAULT_ENCODING) -> str:
    """Calculate the md5 hash for a text."""
    return md5(text.encode(encoding)).hexdigest()  # nosec
