"""Constants"""

from dataclasses import dataclass


@dataclass
class RedisCacheEvents:
    """_summary_"""

    REDIS_CACHE = "REDIS_CACHE"
    CACHE_ERROR = f"{REDIS_CACHE}: Cache error"
    TIMEOUT_CONNECTION = f"{REDIS_CACHE}: Redis connection timed out. Reconnecting."
    ERROR_CONNECTION = f"{REDIS_CACHE}: Error connecting from redis"
    ERROR_DISCONNECTING = f"{REDIS_CACHE}: Error disconnecting from redis"
    NO_CONTEXT_FOUND = f"{REDIS_CACHE}: No context found for:"
    GET_CACHE_ERROR = f"{REDIS_CACHE}: Could not get cache value"
    UNPICKLE_CACHE_ERROR = f"{REDIS_CACHE}: Could not unpickle cache value"
    SET_CACHE_ERROR = f"{REDIS_CACHE}: Could not set value in cache"
    POP_METHOD_CACHE_ERROR = f"{REDIS_CACHE}: Could not pop method cache values"
    POP_CACHE_ERROR = f"{REDIS_CACHE}: Could not pop cache value"
