"""Cache Manager"""

from django.conf import settings

from django_auxilium.utils.functools import (
    BaseCache,
    Caching,
    MemoizeDecorator,
    MemoizeDescriptor,
    NotInCache,
)

from swifty.logging.logger import SwiftyLoggerMixin
from swifty.utils.mapper import getpath

from swifty.utils.importer import import_module_attribute
from swifty.cache.constants import SwiftyCacheEvents


class SwiftyCacheDescriptor(MemoizeDescriptor, SwiftyLoggerMixin):
    """Descriptor for caching with custom parameters."""

    cache_attribute_pattern: str = "{name}"

    def __init__(
        self,
        *args,
        ttl: int = None,
        static_key: str = None,
        vary_by: tuple = (),
        context_getter: str = None,
        **kwargs,
    ):
        self.ttl = ttl

        self.static_key = static_key

        self.vary_by = vary_by
        self.context_getter = context_getter
        super().__init__(*args, **kwargs)

    @staticmethod
    def default_cache_class(*args, **kwargs):
        """Instantiate cache backend."""
        return get_cache_backend()(*args, **kwargs)  # type: ignore

    def get_cache(self, instance) -> Caching:
        """Get cache implementation with custom parameters."""

        return self.cache_class(
            instance,
            self.cache_attribute,
            ttl=self.ttl or getpath(instance, "redis_cache_pattern.ttl", 3600),
            static_key=self.static_key,  # type: ignore
            vary_by=(
                self.vary_by or getpath(instance, "redis_cache_pattern.vary", "")
            ),  # type: ignore
            context_getter=self.context_getter,  # type: ignore
        )

    def getter(self, instance, *args, new_cache: bool = None, **kwargs) -> any:
        """Return cached value or compute and store it."""

        cache_instance = self.get_cache(instance)

        try:
            if new_cache:

                self.logger.debug(
                    f"{SwiftyCacheEvents.CREATE_NEW_CACHE}",
                    cached_function=getpath(cache_instance, "attr", None),
                    args=args,
                    kwargs=kwargs,
                )
                raise NotInCache

            cached_data = cache_instance.get(*args, **kwargs)
            self.logger.debug(
                f"{SwiftyCacheEvents.CACHED_DATA}",
                cached_function=getpath(cache_instance, "attr", None),
                data=cached_data,
                args=args,
                kwargs=kwargs,
            )
            return cached_data

        except NotInCache:

            self.logger.debug(
                f"{SwiftyCacheEvents.DATA_NOT_IN_CACHE}",
                caching_function=getpath(cache_instance, "attr", None),
                args=args,
                kwargs=kwargs,
            )

            return cache_instance.set(
                self.method(instance, *args, **kwargs), *args, **kwargs
            )


class SwiftyCacheDecorator(MemoizeDecorator, SwiftyLoggerMixin):
    """Decorator for caching with custom parameters."""

    cache_descriptor_class = SwiftyCacheDescriptor

    def __init__(
        self,
        ttl: int = None,
        static_key: str = None,
        vary_by: tuple = (),
        context_getter: str = "context",
        is_method: bool = False,
        as_property: bool = False,
    ):
        self.ttl = ttl
        self.static_key = static_key

        self.vary_by = vary_by

        self.context_getter = context_getter

        self.as_property = as_property

        super().__init__(is_method)

    @staticmethod
    def cache_class(*args, **kwargs):
        """Instantiate cache backend."""
        return get_cache_backend()(*args, **kwargs)  # type: ignore

    def get_cache_descriptor(self) -> SwiftyCacheDescriptor:
        """Instantiate cache descriptor with custom parameters."""

        return self.cache_descriptor_class(
            self.to_wrap,
            ttl=self.ttl,
            static_key=self.static_key,
            vary_by=self.vary_by,
            context_getter=self.context_getter,
            as_property=self.as_property,
        )


def get_cache_backend() -> BaseCache:
    """Get the correct cache backend as configured in settings."""

    if not hasattr(settings, "CACHE_BACKEND"):
        # pylint: disable=import-outside-toplevel
        from swifty.redis.cache import RedisCache

        return RedisCache

    return import_module_attribute(settings.CACHE_BACKEND)


cache = SwiftyCacheDecorator.as_decorator()
cache_property = SwiftyCacheDecorator.as_decorator(as_property=True)
