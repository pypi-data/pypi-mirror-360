"""ViewSets"""

from typing import Any, List
from six import text_type
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpRequest
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from swifty.viewsets.constants import LogEvents
from swifty.viewsets.exceptions import JsonException
from swifty.contexts.request_context import RequestContext
from swifty.logging.logger import SwiftyLoggerMixin
from swifty.auth.permissions import SwiftyPermission


class SwiftyViewSet(ViewSet, SwiftyLoggerMixin):
    """A view set that integrates JWT authentication and custom logging."""

    response: Response
    renderer_classes: tuple = (JSONRenderer,)
    authentication_classes: tuple = (JWTAuthentication,)
    permission_classes: tuple = (SwiftyPermission,)

    def initialize_request(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpRequest:
        """Initializes the request object.

        Args:
            request (HttpRequest): The incoming request.

        Returns:
            HttpRequest: The initialized request.
        """
        if not getattr(request, "is_initialized", False):
            request = super().initialize_request(request, *args, **kwargs)
            setattr(request, "is_initialized", True)
        return request

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        """Dispatches the request to the appropriate handler.

        Args:
            request (HttpRequest): The incoming request.

        Returns:
            Response: The response from the view.
        """
        request = self.initialize_request(request, *args, **kwargs)
        with RequestContext(logger=self.logger, request_data=request):
            return super().dispatch(request, *args, **kwargs)

    def handle_exception(self, exc: Exception) -> Response:
        """Handles exceptions raised during request processing.

        Args:
            exc (Exception): The exception raised.

        Returns:
            Response: A JSON response with the error details.
        """
        self.logger.error(LogEvents.EXCEPTION_HANDLER, exceptions=text_type(exc))
        if isinstance(exc, JsonException):
            return JsonResponse(
                getattr(exc, "message", exc.__dict__),
                status=getattr(
                    exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )
        return super().handle_exception(exc)

    def get_permissions(self) -> List[BasePermission]:
        """Returns the list of permissions required for this view.

        Returns:
            List[BasePermission]: The list of permission instances.
        """
        action = self.action and getattr(self, self.action, None)
        permission_classes = (
            getattr(action, "permission_classes", self.permission_classes)
            if action
            else ()
        )
        return [permission() for permission in permission_classes or ()]

    def get_authenticators(self) -> List[BaseAuthentication]:
        """Returns the list of authenticators that this view can use.

        Returns:
            List[BaseAuthentication]: The list of authenticator instances.
        """
        action = getattr(
            self, self.action_map.get(self.request.method.lower(), ""), None
        )  # type: ignore
        authentication_classes = (
            getattr(action, "authentication_classes", self.authentication_classes)
            if action
            else ()
        )
        return [auth() for auth in authentication_classes or ()]

    def perform_authentication(self, request: HttpRequest) -> User:
        """Performs authentication on the request.

        Args:
            request (HttpRequest): The incoming request.

        Raises:
            NotAuthenticated: If authentication fails.

        Returns:
            User: The authenticated user.
        """
        if request.authenticators:
            try:
                getattr(request, "_authenticate")()
            except (TokenError, InvalidToken) as exc:
                raise AuthenticationFailed from exc

            if not request.user or not request.user.is_authenticated:
                raise NotAuthenticated

            return request.user
