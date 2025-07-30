import hashlib
import json
from typing import Any, List, Tuple, Union

from optimas.utils.logger import setup_logger

logger = setup_logger(__name__)


def hash_obj(obj: Any) -> str:
    """
    Compute a deterministic hash for a given object using MD5.

    Args:
        obj (Any): Object to hash. Supports dict, list, tuple, str, or any JSON-serializable type.

    Returns:
        str: Hash string (MD5 hex digest).
    """
    try:
        obj_str = json.dumps(obj, sort_keys=True)  # Ensure consistent ordering
    except TypeError:
        logger.warning(f"Object not JSON-serializable: {obj!r}. Falling back to str().")
        obj_str = str(obj)
    return hashlib.md5(obj_str.encode()).hexdigest()


def is_same(obj1: Any, obj2: Any) -> bool:
    """
    Compare two objects for equality using their hash representations.

    Args:
        obj1 (Any): First object.
        obj2 (Any): Second object.

    Returns:
        bool: True if objects are equal in content, False otherwise.

    Example:
        >>> is_same({"a": 1}, {"a": 1})
        True
        >>> is_same([1, 2], [2, 1])
        False
    """
    return hash_obj(obj1) == hash_obj(obj2)


def unique_objects(obj_list: List[Any], return_idx: bool = False) -> Union[List[Any], Tuple[List[Any], List[int]]]:
    """
    Return a list of unique objects, preserving order.

    Args:
        obj_list (List[Any]): List of hashable or serializable objects.
        return_idx (bool, optional): If True, also return indices of first occurrences. Defaults to False.

    Returns:
        List[Any] or Tuple[List[Any], List[int]]: Unique objects, optionally with their original indices.

    Example:
        >>> data = [{"a": 1}, {"a": 1}, [1, 2], [1, 2], "x", "x"]
        >>> unique_objects(data)
        [{'a': 1}, [1, 2], 'x']

        >>> unique_objects(data, return_idx=True)
        ([{'a': 1}, [1, 2], 'x'], [0, 2, 4])
    """
    seen_hashes = set()
    unique_list = []
    idx_list = []

    for idx, obj in enumerate(obj_list):
        obj_hash = hash_obj(obj)
        if obj_hash not in seen_hashes:
            seen_hashes.add(obj_hash)
            unique_list.append(obj)
            idx_list.append(idx)

    return (unique_list, idx_list) if return_idx else unique_list
