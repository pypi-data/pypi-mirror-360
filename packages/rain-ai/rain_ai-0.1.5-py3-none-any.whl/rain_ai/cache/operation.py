from typing import Any

from cachetools import Cache


def has_key_in_cache(cache: Cache, key: str) -> bool:
    """
    检查缓存中是否存在指定的键

    Args:
        cache (Cache): 缓存实例
        key (str): 要检查的键

    Returns:
        bool: 如果键存在于缓存中，则返回True，否则返回False

    """
    return key in cache


def get_max_size_of_cache(cache: Cache) -> float:
    """
    获取缓存的最大容量

    Args:
        cache (Cache): 缓存实例

    Returns:
        int: 返回缓存的最大容量

    """
    return cache.maxsize


def get_current_size_of_cache(cache: Cache) -> float:
    """
    获取缓存当前的大小

    Args:
        cache (Cache): 缓存实例

    Returns:
        int: 返回缓存当前的大小

    """
    return cache.currsize


def get_value_from_cache(cache: Cache, key: str) -> Any:
    """
    从缓存中获取指定键的值

    Args:
        cache (Cache): 缓存实例
        key (str): 要获取值的键

    Returns:
        Any: 如果键存在于缓存中，则返回对应的值，否则返回None

    """
    return cache.get(key)


def add_value_to_cache(cache: Cache, key: str, value: Any) -> None:
    """
    将指定的键值对添加到缓存中

    Args:
        cache (Cache): 缓存实例
        key (str): 要添加的键
        value (Any): 要添加的值

    Returns:
        None

    """
    cache[key] = value


def remove_key_from_cache(cache: Cache, key: str) -> None:
    """
    从缓存中移除指定的键

    Args:
        cache (Cache): 缓存实例
        key (str): 要移除的键

    Returns:
        None

    """
    if key in cache:
        del cache[key]


__all__ = [
    "has_key_in_cache",
    "get_max_size_of_cache",
    "get_current_size_of_cache",
    "get_value_from_cache",
    "add_value_to_cache",
    "remove_key_from_cache",
]
