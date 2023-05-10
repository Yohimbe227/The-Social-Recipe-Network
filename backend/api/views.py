from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import HttpRequest
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated, \
    DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from djoser.views import UserViewSet as DjoserUserViewSet

from core.classes import AddDelView
from recipes.models import Recipe, Tag
from api.serializers import RecipeReadSerializer, RecipeWriteSerializer, \
    TagSerializer, UserSubscribeSerializer
from recipes.pagination import PageLimitPagination
from users.models import Subscriptions

User = get_user_model()


class BaseAPIRootView(APIRootView):
    """Базовые пути API приложения.
    """


class RecipeView(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AllowAny, ]
    ordering_fields = (
        'name',
    )
    # lookup_field = 'id'

    def update(self, *args: list, **kwargs: dict) -> Response:
        """
        Deny access to the PUT method .

        Args:
            *args: not used.
            **kwargs: not used.

        Returns:
            MethodNotAllowed exception.

        """
        raise MethodNotAllowed('PUT', detail='Use PATCH')

    def partial_update(
        self,
        request: HttpRequest,
        *args: list,
        **kwargs: dict,
    ) -> Response:
        """Override Partial Update Code if desired.

        Args:
            request: HTTPRequest.
            *args: not used.
            **kwargs: not used.

        Returns:
            Updated output.

        """
        return super().update(request, *args, **kwargs, partial=True)

    def get_serializer_class(self) -> [
        RecipeReadSerializer, RecipeWriteSerializer,
    ]:
        """Call the desired serializer depending on the type of query.

        Returns:
            Desired serializer.
        """
        if self.action in (
            'list',
            'retrieve',
        ):
            return RecipeReadSerializer
        return RecipeWriteSerializer


class TagView(ModelViewSet):
    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None


class UserViewSet(DjoserUserViewSet, AddDelView):
    """Работает с пользователями.

    ViewSet для работы с пользователми - отображение и
    регистрация.
    Для авторизованных пользователей —
    возможность подписаться на автора рецепта.
    """
    pagination_class = PageLimitPagination
    add_serializer = UserSubscribeSerializer
    permission_classes = (DjangoModelPermissions,)

    @action(
        methods=('post', 'del', 'get'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request: WSGIRequest, id: int | str) -> Response:
        """Создаёт/удалет связь между пользователями.

        Вызов метода через url: */user/<int:id>/subscribe/.

        Args:
            request (HttpRequest): Объект запроса.
            id (int):
                id пользователя, на которого желает подписаться
                или отписаться запрашивающий пользователь.

        Returns:
            Responce: Статус подтверждающий/отклоняющий действие.
        """
        return self._add_del_obj(id, Subscriptions, Q(author__id=id))

    @action(methods=('get',), detail=False)
    def subscriptions(self, request: HttpRequest) -> Response:
        """Список подписок пользоваетеля.

        Вызов метода через url: */user/<int:id>/subscribtions/.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            Responce:
                401 - для неавторизованного пользователя.
                Список подписок для авторизованного пользователя.
        """
        if self.request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Работает с тэгами.

    Изменение и создание тэгов разрешено только админам.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = (AdminOrReadOnly,)
