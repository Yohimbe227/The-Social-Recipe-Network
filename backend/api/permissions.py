from django.contrib.auth import get_user_model
from django.db.models import Model
from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.routers import APIRootView

User = get_user_model()


# class BanPermission(BasePermission):
#     """Базовый класс.
#
#      Проверяется, забанен ли пользователь.
#
#      """
#
#     def has_permission(self, request: HttpRequest, view: APIRootView) -> bool:
#         del view
#         return (
#                 request.method in permissions.SAFE_METHODS
#                 or request.user.is_authenticated
#                 and request.user.is_active
#         )


class IsAdminUser(BasePermission):
    """Access level - only for admin."""

    def has_permission(self, request: HttpRequest,
                       view: APIRootView) -> bool | None:
        del view
        if request.user.is_authenticated:
            return request.user.is_staff
        return None


class AdminOrReadOnly(BasePermission):
    """Access level.

    Get method is available for all users,
    PATCH, DELETE - only for administrator

    """

    def has_permission(self, request: HttpRequest, view: APIRootView) -> bool:
        del view
        if request.user.is_authenticated and request.method in (
                'PATCH',
                'POST',
                'DELETE',
        ):
            return request.user.is_staff
        return request.method == 'GET'


class GetAllowAny(BasePermission):
    """Access level.

    Only Get method is available for all users,

    """

    def has_permission(self, request: HttpRequest, view: APIRootView) -> bool:

        del view
        return request.method == 'GET'


class AuthorAdminOrReadOnly(BasePermission):
    """
    Get method is available for all users.

    POST, PATCH, DELETE - only for author or admin.
    """

    def has_permission(self, request: HttpRequest, view: any) -> bool:
        del view
        return (
                request.method in permissions.SAFE_METHODS or request.user.is_authenticated
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
                or request.user.is_staff
        )


class AuthorUserOrReadOnly(BasePermission):
    """
    Разрешение на создание и изменение только для админа и пользователя.

    Остальным только чтение объекта.
    """

    def has_permission(self, request: HttpRequest, view: any) -> bool:
        del view
        return (
                request.method in ('GET', 'POST',)
        )

    def has_object_permission(
            self,
            request: HttpRequest,
            view: APIRootView,
            obj: Model
    ) -> bool:
        return (
                request.method == 'GET'
                or request.user.is_staff
                or (request.user.is_authenticated
                    and request.user.is_active
                    and request.user == obj.author
                    and request.method == 'POST')
        )


class PostDelIfAuthentificated(BasePermission):
    def has_permission(self, request: HttpRequest, view: APIRootView) -> bool:
        del view
        return (
                request.method in (
            'POST', 'DELETE') and request.user.is_authenticated
        )
