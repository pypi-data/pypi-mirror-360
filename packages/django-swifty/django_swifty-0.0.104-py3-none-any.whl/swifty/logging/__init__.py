"""Swifty logging module"""

from django.conf import settings

if not getattr(settings, "LOGGING", None):
    from swifty.logging.config import get_logging_config

    logging_config = getattr(settings, "SWIFTY_LOGGING_CONFIG", None) or {}
    setattr(settings, "LOGGING", get_logging_config(**logging_config))
