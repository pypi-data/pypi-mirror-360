"""SwiftyLoggerMixin"""

import structlog
from django.conf import settings
from swifty.utils.mapper import getpath


class SwiftyLoggerMixin:
    """Mixin for structured logging."""

    logging_context: dict | None = None

    @property
    def logger(self) -> structlog.BoundLogger:
        """Get the logger instance."""
        name = f"{self.__module__}.{self.__class__.__name__}"
        _logger = structlog.getLogger(name, exc_info=settings.DEBUG)
        if self.logging_context:
            _logger.bind(**(self.logging_context or {}))
        return _logger

    def init_context(self) -> dict:
        """Initialize logging context."""
        return self.logging_context or {}

    @property
    def context(self) -> dict:
        """Get the current logging context."""
        return (
            getpath(self.logger.bind(), "_context._dict") or self.logging_context or {}
        )

    def set_extra_context(self, extra_context: dict) -> None:
        """Bind extra context to the logger."""
        self.logger.bind(**extra_context)


swifty_logger = structlog.get_logger(__name__, exc_info=settings.DEBUG)
