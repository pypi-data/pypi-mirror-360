# -*- coding: utf-8 -*-
"""Redis cache implementation for Swifty providing caching functionality with Redis backend."""

import base64

import os
import pickle
from io import BytesIO
from functools import wraps
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple, Union
import redis

from django.conf import settings
from django_auxilium.utils.functools import BaseCache, NotInCache

from swifty.redis.constants import RedisCacheEvents
from swifty.logging.logger import SwiftyLoggerMixin
from swifty.utils.mapper import getpath


@dataclass
class ClearCacheScope:
    """Defines cache clearing scopes."""

    METHOD = "METHOD"
    PATTERN = "PATTERN"
    ALL = "ALL"


def _redis_reconnect(func: Callable) -> Callable:
    """
    Decorator to automatically reconnect Redis connection on errors.

    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (redis.ConnectionError, redis.TimeoutError):
            self.logger.error(RedisCacheEvents.TIMEOUT_CONNECTION, exc_info=True)
            self.reconnect()
            return func(self, *args, **kwargs)

    return wrapper


class RedisCache(BaseCache, SwiftyLoggerMixin):
    """Redis cache implementation with logging and connection management."""

    DEFAULT_REDIS_CACHE_DB: int = int(os.environ.get("DEFAULT_REDIS_CACHE_DB", 1))
    DEFAULT_REDIS_CACHE_PATTERN: Dict[str, Union[str, int]] = {
        "prefix": "DEFAULT",
        "ttl": 3600,
        "vary_by": [""],
        "db": DEFAULT_REDIS_CACHE_DB,
    }
    REDIS_SESSION_CACHE: str = getattr(
        settings, "REDIS_SESSION_CACHE", "django.contrib.sessions.cache"
    )

    @classmethod
    def redis_connection(cls, pool: redis.ConnectionPool) -> redis.StrictRedis:
        """Establish a Redis connection using the provided connection pool."""
        return redis.StrictRedis(connection_pool=pool)

    @classmethod
    def connect(cls, **kwargs) -> redis.StrictRedis:
        """Get the Redis connection, creating it if necessary."""

        cache_db = getpath(kwargs, "cache_db", cls.DEFAULT_REDIS_CACHE_DB)
        cls.redis = cls.redis_connection(
            pool=settings.REDIS_CONNECTION_POOL.get(f"pool_{cache_db}")
        )
        return cls.redis

    @classmethod
    def close(cls) -> None:
        """Close the Redis connection if it exists."""

        if hasattr(cls, "redis"):
            cls.redis.close()

    @classmethod
    def reconnect(cls) -> redis.StrictRedis:
        """Reconnect to Redis, disconnecting the old connection."""
        if hasattr(cls, "redis"):
            cls.redis.connection_pool.disconnect()
            del cls.redis
        return cls.connect()

    def __init__(
        self,
        parent: Any,
        attr: str,
        ttl: Optional[int] = None,
        static_key: Optional[str] = None,
        vary_by: Tuple[str, ...] = (),
        context_getter: Optional[Callable] = None,
    ) -> None:
        super().__init__(parent, attr)
        self.ttl = ttl
        self.static_key = static_key
        self._vary_by = vary_by
        self.context_getter = context_getter

    def __contains__(self, item: str) -> bool:
        return getpath(self, item, False)

    def add(self, *args: Any, **kwargs: Any) -> Any:
        """Add a value to the cache."""
        return self.set(*args, **kwargs)

    def _get_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate the cache key."""
        return self.static_key or self._generate_key(*args, **kwargs)

    def _generate_key_prefix(self) -> str:
        """Generate the key prefix based on environment and pattern."""

        pattern = self._get_parent_pattern()
        env_prefix = os.environ.get("ENVIRONMENT_NAME")
        return "_".join(filter(None, [env_prefix, pattern["prefix"]]))

    def _get_parent_pattern(self) -> Dict[str, Union[str, int]]:
        """Get the cache pattern from the parent object."""
        return getpath(
            self.parent, "redis_cache_pattern", self.DEFAULT_REDIS_CACHE_PATTERN
        )

    def _generate_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate a unique cache key based on various parameters."""
        parent_name = self.parent.__class__.__name__
        vary_by = self._get_vary_by()
        parameters = (
            base64.b64encode(
                bytes(str(args + (sorted(kwargs.items()),)), encoding="utf-8")
            ).decode("utf-8")
            if args or kwargs
            else None
        )
        return "_".join(
            filter(
                None,
                [
                    self._generate_key_prefix(),
                    parent_name,
                    self.attr,
                    vary_by,
                    parameters,
                ],
            )
        )

    def _get_vary_by(self) -> str:
        """Construct the vary by string from context."""
        context = self.context
        if isinstance(context, str):
            return context
        return (
            "_".join(str(context.get(key)) for key in self.vary_by if context.get(key))
            if context and self.vary_by
            else self.logger.warn(
                f"{RedisCacheEvents.NO_CONTEXT_FOUND} {self.parent.__class__.__name__}"
            )
        )

    @property
    def vary_by(self) -> Tuple[str, ...]:
        """Get the vary by cache string."""
        return self._vary_by or self._get_parent_pattern().get("vary_by")

    @property
    def context(self) -> Any:
        """Get context from the parent object."""
        if callable(self.context_getter):
            return self.context_getter(self.parent)
        return (
            getattr(self.parent, self.context_getter, {})
            if isinstance(self.context_getter, str)
            else getattr(self.parent, "context", {})
        )

    def get(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve a value from the cache."""
        key = self._get_key(*args, **kwargs)
        try:
            value = self._get(key)
            return pickle.load(BytesIO(value))  # type: ignore
        except NotInCache:
            raise
        except Exception as error:
            self.logger.error(
                event_name=RedisCacheEvents.GET_CACHE_ERROR,
                key=key or "<could not compute cache key>",
                method=self.attr,
                parent=self.parent.__class__.__name__,
                error=error,
                exc_info=True,
            )
            raise NotInCache from error

    def set(self, value: Any, *args: Any, **kwargs: Any) -> Any:
        """Store a value in the cache after pickling it."""
        key = self._get_key(*args, **kwargs)
        encoded = pickle.dumps(value)
        self._set(key, encoded)
        return value

    def delete(self, *args: Any, **kwargs: Any) -> Optional[Any]:
        """Delete a value from the cache."""
        if (args, kwargs) == ((ClearCacheScope.METHOD,), {}):
            return self._delete_method()
        if (args, kwargs) == ((ClearCacheScope.PATTERN,), {}):
            raise ValueError("Cannot pop cache pattern from instance methods")
        if (args, kwargs) == ((ClearCacheScope.ALL,), {}):
            raise ValueError("Cannot clear cache from instance methods")
        key = self._get_key(*args, **kwargs)
        return self._delete_value(key)

    @_redis_reconnect
    def _get(self, key: str) -> bytes:
        """Retrieve a raw value from Redis."""
        connection = self.connect(
            cache_db=(
                self.parent.redis_cache_pattern.get("db", self.DEFAULT_REDIS_CACHE_DB)
                if hasattr(self.parent, "redis_cache_pattern")
                else 1
            )
        )
        value = connection.get(key)
        if value is None:
            raise NotInCache
        return value

    @_redis_reconnect
    def _set(self, key: str, value: bytes) -> None:
        """Store a raw value in Redis."""
        connection = self.connect(
            cache_db=getpath(
                self.parent,
                "redis_cache_pattern.db",
                self.DEFAULT_REDIS_CACHE_PATTERN["db"],
            )
        )
        ttl = self.ttl or self.DEFAULT_REDIS_CACHE_PATTERN["ttl"]
        connection.set(key, value)
        if ttl:
            connection.expire(key, ttl)

    @_redis_reconnect
    def _delete_value(self, key: str) -> None:
        """Delete a value from Redis."""
        connection = self.connect(
            cache_db=(
                self.parent.redis_cache_pattern.get("db", self.DEFAULT_REDIS_CACHE_DB)
                if hasattr(self.parent, "redis_cache_pattern")
                else self.DEFAULT_REDIS_CACHE_DB
            )
        )
        for full_key in connection.scan_iter(key):
            connection.delete(full_key)

    @_redis_reconnect
    def _delete_method(self) -> None:
        """Delete cache entries for a specific method."""
        connection = self.connect(
            cache_db=(
                self.parent.redis_cache_pattern.get("db", self.DEFAULT_REDIS_CACHE_DB)
                if hasattr(self.parent, "redis_cache_pattern")
                else self.DEFAULT_REDIS_CACHE_DB
            )
        )
        full_pattern = (
            "_".join(
                [
                    os.environ.get("ENVIRONMENT_NAME", ""),
                    self._get_parent_pattern()["prefix"],
                    self.parent.__class__.__name__,
                    self.attr,
                ]
            )
            + "*"
        )

        for key in connection.scan_iter(full_pattern):
            connection.delete(key)
