"""Permissions"""

from typing import Any, Dict, List, Optional, Union, Callable
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet
from swifty.logging.logger import SwiftyLoggerMixin
from swifty.utils.mapper import get_nested_attributes
from swifty.auth.constants import LogEvents


class SwiftyPermission(BasePermission, SwiftyLoggerMixin):
    """Permission class that checks user attributes against allowed values."""

    permission_layers: Optional[List[Dict[str, Union[str, List[Any], Callable]]]] = None

    def has_permission(self, request: Request, view: ViewSet) -> bool:
        """Check if user has required permissions based on permission_layers."""
        try:
            if isinstance(request.user, AnonymousUser):
                raise PermissionDenied

            for layer in self.permission_layers or []:
                if (
                    not (path := layer.get("path"))
                    or not (allowed := layer.get("allowed"))
                    or allowed is True
                ):
                    continue

                allowed = allowed(request, view) if callable(allowed) else allowed
                if get_nested_attributes(root=request.user, path=path) not in allowed:
                    raise PermissionDenied

            return True

        except (PermissionDenied, AttributeError, TypeError) as error:
            self.logger.error(LogEvents.PERMISSIONS_DENIED_BY_ERROR, error=error)
            return False
