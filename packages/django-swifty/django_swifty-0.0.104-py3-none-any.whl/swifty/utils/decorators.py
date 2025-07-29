"""Decorators"""

from typing import Callable
from functools import wraps


def once_trigger(func: Callable) -> Callable:
    """Decorator to ensure a method is only called once per instance."""

    @wraps(func)
    def wrapper(self):
        saved_name = f"_{self.__class__.__name__}_{func.__name__}"
        if not hasattr(self, saved_name):
            setattr(self, saved_name, func(self))
        return getattr(self, saved_name)

    return wrapper
