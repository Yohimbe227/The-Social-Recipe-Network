from datetime import datetime as dt

from api.permissions import AdminOrReadOnly, AuthorAdminOrReadOnly, \
    AuthorUserOrReadOnly, PostDelIfAuthentificated, GetAllowAny
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             SmallRecipeSerializer, TagSerializer,
                             UserSubscribeSerializer)
from backend.settings import DATE_TIME_FORMAT
from core.classes import AddDelView
from core.constants import (SYMBOL_FALSE_SEARCH, SYMBOL_TRUE_SEARCH, Queries)
from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import F, Q, QuerySet, Sum
from django.http import HttpRequest
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import Carts, Favorites, Ingredient, Recipe, Tag
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Subscriptions
from core.constants import Methods
User = get_user_model()


class BaseAPIRootView(APIRootView):
    """Базовые пути API приложения."""


class RecipeViewSet(ModelViewSet, AddDelView):
    """Обработка рецептов.

    Вывод, создание, редактирование, добавление/удаление
    в избранное и список покупок.
    Отправка текстового файла со списком покупок.
    Для авторизованных пользователей — возможность добавить
    рецепт в избранное и в список покупок.
    Изменять рецепт может только автор или админы.
    """

    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (AuthorAdminOrReadOnly,)
    add_serializer = SmallRecipeSerializer

    def get_queryset(self) -> QuerySet[Recipe]:
        """Получает `queryset` в соответствии с параметрами запроса.

        Returns:
            `QuerySet`: Список запрошенных объектов.
        """
        queryset = self.queryset

        tags: list = self.request.query_params.getlist(Queries.TAGS)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        if self.request.user.is_anonymous:
            return queryset

        is_in_cart = self.request.query_params.get(Queries.SHOP_CART)
        if is_in_cart in SYMBOL_TRUE_SEARCH:
            queryset = queryset.filter(in_carts__user=self.request.user)
        elif is_in_cart in SYMBOL_FALSE_SEARCH:
            queryset = queryset.exclude(in_carts__user=self.request.user)

        is_favorite = self.request.query_params.get(Queries.FAVORITE)
        if is_favorite in SYMBOL_TRUE_SEARCH:
            queryset = queryset.filter(in_favorites__user=self.request.user)
        if is_favorite in SYMBOL_FALSE_SEARCH:
            queryset = queryset.exclude(in_favorites__user=self.request.user)

        return queryset

    @action(
        methods=Methods.ACTION_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request: HttpRequest, pk: int | str) -> Response:
        """Добавляет/удалет рецепт в `избранное`.

        Args:
            request: Объект запроса.
            pk:
                id рецепта, который нужно добавить/удалить из `избранного`.

        Returns:
            Responce: Статус подтверждающий/отклоняющий действие.
        """
        return self._add_del_obj(pk, Favorites, Q(recipe__id=pk))

    @action(
        methods=(
            "get",
            "post",
            "delete",
        ),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request: HttpRequest, pk: int | str) -> Response:
        """Добавляет/удалет рецепт в `список покупок`.

        Вызов метода через url: */recipe/<int:pk>/shopping_cart/.

        Args:
            request: Объект запроса.
            pk: id рецепта, который нужно добавить/удалить в `корзину покупок`.

        Returns:
            Responce: Статус подтверждающий/отклоняющий действие.

        """
        return self._add_del_obj(pk, Carts, Q(recipe__id=pk))

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request: HttpRequest) -> HttpResponse:
        """Загружает файл *.txt со списком покупок.

        Считает сумму ингредиентов в рецептах выбранных для покупки.
        Возвращает текстовый файл со списком ингредиентов.
        Вызов метода через url:  */recipes/download_shopping_cart/.

        Args:
            request (HttpRequest): Объект запроса..

        Returns:
            Responce: Ответ с текстовым файлом.

        """
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = [
            f'Список покупок для:\n{user.first_name}'
            f'{dt.now().strftime(DATE_TIME_FORMAT)}\n'
        ]

        ingredients = (
            Ingredient.objects.filter(recipe__recipe__in_carts__user=user)
            .values('name', measurement=F('measurement_unit'))
            .annotate(amount=Sum('recipe__amount'))
        )

        for ing in ingredients:
            shopping_list.append(f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}')

        shopping_list.append('\nПосчитано в Foodgram')
        shopping_list = '\n'.join(shopping_list)
        response = HttpResponse(shopping_list, content_type='text.txt; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class UserViewSet(DjoserUserViewSet, AddDelView):
    """Работает с пользователями.

    ViewSet для работы с пользователми - отображение и
    регистрация.
    Для авторизованных пользователей —
    возможность подписаться на автора рецепта.
    """

    pagination_class = PageLimitPagination
    add_serializer = UserSubscribeSerializer
    permission_classes = (AuthorUserOrReadOnly,)

    @action(
        methods=Methods.ACTION_METHODS,
        detail=True,
        permission_classes=(PostDelIfAuthentificated,),
    )
    def subscribe(self, request: HttpRequest, id: int | str) -> Response:
        """Создаёт/удалет связь между пользователями.

        Вызов метода через url: */user/<int:id>/subscribe/.

        Args:
            request: Объект запроса.
            id:
                id пользователя, на которого желает подписаться
                или отписаться запрашивающий пользователь.

        Returns:
            Responce: Статус подтверждающий/отклоняющий действие.
        """
        return self._add_del_obj(id, Subscriptions, Q(author__id=id))

    @action(methods=('get',), detail=False)
    def subscriptions(self, request: HttpRequest) -> Response:
        """Список подписок пользоваетеля.

        Вызов метода через url: */user/<int:id>/subscriptions/.

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

    @action(['get', ], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)


class TagViewSet(ReadOnlyModelViewSet):
    """Работает с тэгами.

    Изменение и создание тэгов разрешено только админам.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (GetAllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Работает с тэгами.

    Изменение и создание тэгов разрешено только админам.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
