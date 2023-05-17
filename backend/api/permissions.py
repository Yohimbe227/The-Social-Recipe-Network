from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.routers import APIRootView

User = get_user_model()


class AdminOrReadOnly(BasePermission):
    """Access level.

    Get method is available for all users,
    PATCH, POST, DELETE - only for administrator

    """

    def has_permission(self, request: HttpRequest, view: APIRootView) -> bool:
        return request.method in SAFE_METHODS or request.user.is_staff


class AuthorOrReadOnly(BasePermission):
    """
    Get method is available for all users.

    POST, PATCH, DELETE - only for author or admin.

    """

    def has_permission(self, request: HttpRequest, view: APIRootView) -> bool:
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(
        self,
        request: HttpRequest,
        view: APIRootView,
        obj: User,
    ) -> bool:
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
