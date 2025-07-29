"""Utility module for mapping and accessing nested data structures through path expressions."""

from typing import Any, Dict, List, Optional, Union, Generator
import re
import six

PATH_DELIMITERS = [",", ".", "[", "]"]


def parse_path(path: Union[str, List[str]]) -> Generator[str, None, None]:
    """Parse a path string or list into individual keys.
    Args:
        path (Union[str, List[str]]): The path to parse.
    Yields:
        str: Individual keys from the path.
    """

    if isinstance(path, six.string_types):
        path = _split_and_trim(path, *PATH_DELIMITERS)
    for key in path:
        if isinstance(key, six.string_types):
            yield from _split_and_trim(key, *PATH_DELIMITERS)
        else:
            yield key


def _split_and_trim(string: str, *delimiters: str) -> List[str]:
    """Split a string by given delimiters and trim empty results.
    Args:
        string (str): The string to split.
        *delimiters (str): Delimiters to use for splitting.
    Returns:
        List[str]: List of non-empty substrings.
    """
    pattern = "|".join(map(re.escape, delimiters))
    return list(filter(None, re.split(pattern, string)))


def getpath(
    obj: Union[Dict, List, Any],
    path: Union[str, List[str]],
    default: Optional[Any] = None,
) -> Any:
    """Retrieve a value from a nested structure using a path.
    Args:
        obj (Union[Dict, List, Any]): The object to search.
        path (Union[str, List[str]]): The path to follow.
        default (Optional[Any]): The value to return if the path does not exist.
    Returns:
        Any: The value found at the path or the default value.
    """

    for key in parse_path(path):
        try:
            obj = getattr(obj, key) if hasattr(obj, key) else obj[key]
        except (KeyError, IndexError, TypeError, AttributeError):
            return default
        if obj is None:
            break
    return obj


def get_nested_attributes(root: Any, path: str, default: Optional[Any] = None) -> Any:
    """Get nested attributes from an object using a dot-separated path.
    Args:
        root (Any): The root object to search.
        path (str): The dot-separated path to follow.
        default (Optional[Any]): The value to return if the path does not exist.
    Returns:
        Any: The value found at the path or the default value.
    """
    try:
        return six.moves.reduce(getattr, [root] + path.split("."))
    except AttributeError:
        return default
