"""Exceptions ViewSets"""

from typing import Any
from rest_framework.status import HTTP_400_BAD_REQUEST
from six import text_type


class JsonException(Exception):
    """Custom exception for JSON responses."""

    def __init__(self, message: Any, status_code: int = HTTP_400_BAD_REQUEST) -> None:
        self.status_code = status_code
        self.message = (
            {"errors": text_type(message)}
            if not isinstance(message, (dict, list))
            else message
        )
        super().__init__(self.message)
