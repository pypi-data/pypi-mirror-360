"""Set up logging configuration with type hints and improved documentation."""

from typing import Optional, Dict, Any, List
import logging
import structlog


def get_logging_config(
    log_level: int = logging.INFO,
    log_handlers: Optional[List[str]] = None,
    additional_config: Optional[Dict[str, Any]] = None,
    processors: Optional[List[Any]] = None,
    context_class: Optional[Any] = None,
    logger_factory: Optional[Any] = None,
    wrapper_class: Optional[Any] = None,
    cache_logger_on_first_use: bool = True,
) -> Dict[str, Any]:
    """Generate logging configuration.

    Args:
        log_level (int): Logging level for the root logger. Defaults to logging.INFO.
        log_handlers (Optional[List[str]]): List of handlers for the loggers. Defaults to None.
        additional_config (Optional[Dict[str, Any]]): Additional configuration. Defaults to None.
        processors (Optional[List[Any]]): List of processors for structlog. Defaults to None.
        context_class (Optional[Any]): Context class for structlog. Defaults to None.
        logger_factory (Optional[Any]): Logger factory for structlog. Defaults to None.
        wrapper_class (Optional[Any]): Wrapper class for structlog. Defaults to None.
        cache_logger_on_first_use (bool): Whether to cache logger on first use. Defaults to True.

    Returns:
        Dict[str, Any]: The logging configuration dictionary.
    """

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
            },
            "plain_console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
            },
            "key_value": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.KeyValueRenderer(
                    key_order=["timestamp", "level", "event", "logger", "func_name"],
                ),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "plain_console",
            }
        },
        "loggers": {
            "django": {
                "handlers": log_handlers or ["console"],
                "level": logging.CRITICAL,
                "propagate": False,
            },
            "root": {
                "handlers": log_handlers or ["console"],
                "level": log_level,
                "propagate": False,
            },
        },
    }

    if additional_config:
        logging_config.update(additional_config)

    structlog.configure(
        processors=processors
        or [
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.CallsiteParameterAdder(
                [structlog.processors.CallsiteParameter.FUNC_NAME],
            ),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=context_class or structlog.threadlocal.wrap_dict(dict),
        logger_factory=logger_factory or structlog.stdlib.LoggerFactory(),
        wrapper_class=wrapper_class or structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=cache_logger_on_first_use,
    )

    return logging_config
