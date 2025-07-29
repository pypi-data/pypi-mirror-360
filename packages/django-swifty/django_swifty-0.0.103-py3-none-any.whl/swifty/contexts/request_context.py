"""Request Context"""

from typing import Dict, Any
from django.conf import settings
from swifty.utils.mapper import getpath


class RequestContext:
    """Context manager for handling request data.

    Args:
        logger: Logger instance for logging context.
        request_data: Dictionary containing request data.

    Returns:
        None
    """

    context_fields: tuple = (
        ("user.username", "username"),
        ("user.id", "user_id"),
        ("user.role_level", "user_role_level"),
        ("method", "method"),
        ("resolver_match.app_name", "app_name"),
        ("path", "path"),
        ("resolver_match.url_name", "url_name"),
    )

    def __init__(self, logger: Any, request_data: Dict[str, Any]) -> None:
        self.logger = logger
        self.request_data = request_data or {}
        self.request_context: Dict[str, Any] = {}

    @property
    def context_fields_mapping(self) -> tuple:
        """Get context fields mapping.

        Returns:
            tuple: Context fields mapping.
        """
        return getattr(settings, "CONTEXT_FIELDS_MAPPING", self.context_fields)

    def __enter__(self) -> "RequestContext":
        self.request_context = {
            field[1]: getpath(self.request_data, field[0])
            for field in self.context_fields_mapping
            if getpath(self.request_data, field[0])
        }
        self.logger.bind(**self.request_context)
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self.logger.unbind(*self.request_context.keys())


# class SetContextInstance:
#     def __init__(self, instance, class_base):
#         self.class_base = class_base
#         self.class_context = getattr(class_base, "context", None)
#         self.instance_context = getattr(instance, "context", {})
#         self.initial_class_context = deepcopy(self.class_context)

#     def __enter__(self):
#         if isinstance(self.class_context, dict):
#             self.class_base.context.update(self.instance_context)
#         else:
#             setattr(self.class_base, "context", self.instance_context)

#     def __exit__(self):
#         setattr(self.class_base, "context", self.initial_class_context)
