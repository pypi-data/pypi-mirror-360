from cachetools import Cache, LRUCache, TTLCache, LFUCache, RRCache, FIFOCache


def create_cache(maxsize: int) -> Cache:
    """
    创建一个基本缓存
    Args:
        maxsize (int): 缓存的最大容量

    Returns:
        Cache: 返回一个Cache实例

    """
    return Cache(maxsize)


def create_lru_cache(maxsize: int) -> Cache:
    """
    创建一个基于LRU（最少使用）算法的缓存

    Args:
        maxsize (int): 缓存的最大容量

    Returns:
        Cache: 返回一个LRUCache实例

    """

    return LRUCache(maxsize)


def create_lfu_cache(maxsize: int) -> Cache:
    """
    创建一个基于LFU（最少访问）算法的缓存

    Args:
        maxsize (int): 缓存的最大容量

    Returns:
        Cache: 返回一个LFUCache实例

    """
    return LFUCache(maxsize)


def create_ttl_cache(maxsize: int, ttl: int) -> Cache:
    """
    创建一个基于TTL（时间到期）算法的缓存

    Args:
        maxsize (int): 缓存的最大容量
        ttl (int): 缓存项的生存时间（以秒为单位）

    Returns:
        Cache: 返回一个TTLCache实例

    """

    return TTLCache(maxsize, ttl=ttl)


def create_rr_cache(maxsize: int) -> Cache:
    """
    创建一个基于RR（随机替换）算法的缓存

    Args:
        maxsize (int): 缓存的最大容量

    Returns:
        Cache: 返回一个RRCache实例

    """

    return RRCache(maxsize)


def create_fifo_cache(maxsize: int) -> Cache:
    """
    创建一个基于FIFO（先进先出）算法的缓存

    Args:
        maxsize (int): 缓存的最大容量

    Returns:
        Cache: 返回一个FIFOCache实例

    """
    return FIFOCache(maxsize)


__all__ = [
    "create_cache",
    "create_lru_cache",
    "create_lfu_cache",
    "create_ttl_cache",
    "create_rr_cache",
    "create_fifo_cache",
]
