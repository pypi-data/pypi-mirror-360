"""Importer"""

from typing import Any
from importlib import import_module


def import_module_attribute(import_string: str, package: str = None) -> Any:
    """Import a module or attribute from a module."""
    try:
        return import_module(import_string, package)
    except ImportError:
        module, attr = import_string.rsplit(".", 1)
        return getattr(import_module(module, package), attr)
