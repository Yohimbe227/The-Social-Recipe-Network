from django.contrib.auth import get_user_model
from django.db.models import F, Q, QuerySet, Sum
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.utils import timezone
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilterBackend
from api.permissions import AdminOrReadOnly, AuthorOrReadOnly
from api.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    SmallRecipeSerializer,
    TagSerializer,
    UserSubscribeSerializer,
)
from backend.settings import DATE_TIME_FORMAT
from core.classes import AddDelView
from core.constants import Additional, Methods
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from users.models import Subscriptions

User = get_user_model()


class RecipeViewSet(ModelViewSet, AddDelView):
    """Обработка рецептов.

    Вывод, создание, редактирование, добавление/удаление в избранное и список
    покупок.
    Отправка текстового файла со списком покупок.
    Для авторизованных пользователей — возможность добавить рецепт в избранное
    и в список покупок.
    Изменять рецепт может только автор или админы.

    """

    queryset = Recipe.objects.select_related('author')
    permission_classes = (AuthorOrReadOnly,)
    add_serializer = SmallRecipeSerializer

    def perform_create(
        self,
        serializer: RecipeReadSerializer,
    ) -> None:
        """Добавляем автора в вывод."""

        serializer.save(author=self.request.user)

    def get_queryset(self) -> QuerySet[Recipe]:
        """Получает `queryset` в соответствии с параметрами запроса.

        Returns:
            `QuerySet`: Список запрошенных объектов.

        """
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        if self.request.user.is_anonymous:
            return queryset

        is_in_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_cart in Additional.SYMBOL_TRUE_SEARCH:
            queryset = queryset.filter(shopping_cart__user=self.request.user)
        elif is_in_cart in Additional.SYMBOL_FALSE_SEARCH:
            queryset = queryset.exclude(shopping_cart__user=self.request.user)

        is_favorite = self.request.query_params.get('is_favorited')
        if is_favorite in Additional.SYMBOL_TRUE_SEARCH:
            queryset = queryset.filter(in_favorites__user=self.request.user)
        if is_favorite in Additional.SYMBOL_FALSE_SEARCH:
            queryset = queryset.exclude(in_favorites__user=self.request.user)

        return queryset

    @action(
        methods=Methods.GET_POST_DEL_METHODS,
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
        return self._add_del_obj(pk, Favorite, Q(recipe__id=pk))

    @action(
        methods=(
            'get',
            'post',
            'delete',
        ),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request: HttpRequest, pk: int | str) -> Response:
        """Добавляет/удалет рецепт в `список покупок`.

        Args:
            request: Объект запроса.
            pk: id рецепта, который нужно добавить/удалить в `корзину покупок`.

        Returns:
            Responce: Статус подтверждающий/отклоняющий действие.

        """
        return self._add_del_obj(pk, Cart, Q(recipe__id=pk))

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request: HttpRequest) -> HttpResponse:
        """Загружает файл *.txt со списком покупок.

        Считает сумму ингредиентов в рецептах выбранных для покупки.
        Возвращает текстовый файл со списком ингредиентов.
        Вызов метода через url:  */recipes/download_shopping_cart/.

        Args:
            request: Объект запроса..

        Returns:
            Responce: Ответ с текстовым файлом.

        """
        user = self.request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = [
            f'Список покупок для: {user.first_name} '
            f'\n{timezone.now().strftime(DATE_TIME_FORMAT)}\n',
        ]

        ingredients = (
            Ingredient.objects.filter(
                ingredientrecipes__recipe__shopping_cart__user=user,
            )
            .values('name', measurement=F('measurement_unit'))
            .annotate(amount=Sum('ingredientrecipes__amount'))
        )

        for ing in ingredients:
            shopping_list.append(
                f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}',
            )

        shopping_list.append('\nХороших покупок!')
        shopping_list = '\n'.join(shopping_list)
        response = HttpResponse(
            shopping_list,
            content_type='text.txt; charset=utf-8',
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def get_serializer_class(
        self,
    ) -> [RecipeReadSerializer | RecipeWriteSerializer]:
        """Выбор сериализатора в зависимости от вида запроса.

        Returns:
            Выбранный сериализатор.

        """
        if self.action in (
            'list',
            'retrieve',
        ):
            return RecipeReadSerializer
        return RecipeWriteSerializer


class UserViewSet(DjoserUserViewSet, AddDelView):
    """Работает с пользователями.

    ViewSet для работы с пользователми - отображение и регистрация.
    Для авторизованных пользователей — возможность подписаться на автора
    рецепта.

    """

    add_serializer = UserSubscribeSerializer
    permission_classes = (AuthorOrReadOnly,)

    @action(
        methods=Methods.GET_POST_DEL_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,),
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
            User.objects.filter(subscribers__user=self.request.user),
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        ('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)


class TagViewSet(ReadOnlyModelViewSet):
    """Работает с тэгами.

    Изменение и создание тэгов разрешено только админам.

    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Работает с ингредиентами.

    Изменение и создание тэгов разрешено только админам.

    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    filter_backends = (IngredientFilterBackend,)
    search_fields = ('name',)
