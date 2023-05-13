import base64
from http import HTTPStatus

from rest_framework.exceptions import ValidationError

from core.utils import recipe_ingredients_set
from django.contrib.auth import get_user_model
from django.db.models import F, QuerySet
from drf_extra_fields.fields import Base64ImageField

from core.validators import tags_exist_validator, ingredients_validator
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

User = get_user_model()


class SmallRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe.

    Уменьшенный набор полей для некоторых эндпоинтов.
    """

    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = ('__all__',)


class TagSerializer(serializers.ModelSerializer):
    # def validate_color(self, color: str) -> str:
    #     """Проверка формата цвета.
    #
    #     Args:
    #         color: Цвет тэга.
    #
    #     Returns:
    #         Цвет тэга (проверено).
    #
    #     Raises:
    #          ValidationError: Введите корректный цвет!
    #
    #     """
    #     if color[0] != '#' or len(color) != 7:
    #         raise serializers.ValidationError('This is not a color in HEX format')
    #     return color

    def validate(self, data: dict) -> dict:
        """Унификация вводных данных при создании/редактировании тэга.

        Args:
            data: Входные данные.

        Returns:
            data: Валидированные данные.
        """
        for attr, value in data.items():
            data[attr] = value.sttrip(' #').upper()
        return data

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для использования с моделью User."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj: User) -> bool:
        """Проверка подписки пользователей.

        Определяет - подписан ли текущий пользователь
        на просматриваемого пользователя.

        Args:
            obj: Пользователь, на которого проверяется подписка.

        Returns:
            bool: True, если подписка есть. Во всех остальных случаях False.
        """
        if self.context.get('request'):
            user = self.context.get('request').user
        else:
            return False

        if user.is_anonymous or (user == obj):
            return False

        return user.subscriptions.filter(author=obj).exists()

    def create(self, validated_data: dict) -> User:
        """Создаёт нового пользователя с запрошенными полями.

        Args:
            validated_data (dict): Полученные проверенные данные.

        Returns:
            User: Созданный пользователь.
        """
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class RecipeSerializer(ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_ingredients(self, recipe: Recipe) -> QuerySet[dict]:
        """Получает список ингридиентов для рецепта.

        Args:
            recipe: Запрошенный рецепт.

        Returns:
            QuerySet: Список ингридиентов в рецепте.

        """
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe: Recipe) -> bool:
        """Проверка - находится ли рецепт в избранном.

        Args:
            recipe (Recipe): Переданный для проверки рецепт.

        Returns:
            bool: True - если рецепт в `избранном`
            у запращивающего пользователя, иначе - False.
        """
        user = self.context.get("view").request.user

        if user.is_anonymous:
            return False

        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        """Проверка - находится ли рецепт в списке  покупок.

        Args:
            recipe: Переданный для проверки рецепт.

        Returns:
            True - если рецепт в `списке покупок`
            у запращивающего пользователя, иначе - False.
        """
        user = self.context.get('view').request.user

        if user.is_anonymous:
            return False

        return user.carts.filter(recipe=recipe).exists()

    def validate(self, data: dict) -> dict:
        """Проверка вводных данных при создании/редактировании рецепта.

        Args:
            data (OrderedDict): Вводные данные.

        Raises:
            ValidationError: Тип данных несоответствует ожидаемому.

        Returns:
            data (dict): Проверенные данные.

        """
        tags_ids: list[int] = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        if not tags_ids or not ingredients:
            raise ValidationError('Недостаточно данных.')

        tags_exist_validator(tags_ids, Tag)
        ingredients = ingredients_validator(ingredients, Ingredient)

        data.update({
            'tags': tags_ids,
            'ingredients': ingredients,
            'author': self.context.get('request').user
        })
        return data

    def create(self, validated_data: dict) -> Recipe:
        """Создаёт рецепт.

        Args:
            validated_data: Данные для создания рецепта.

        Returns:
            Recipe: Созданый рецепт.

        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients_set(recipe, ingredients)
        return recipe

    def update(self, recipe: Recipe, validated_data: dict):
        """Обновляет рецепт.

        Args:
            recipe (Recipe): Рецепт для изменения.
            validated_data (dict): Изменённые данные.

        Returns:
            Recipe: Обновлённый рецепт.
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            recipe_ingredients_set(recipe, ingredients)

        recipe.save()
        return recipe


class CreateUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор вывода авторов на которых подписан текущий пользователь."""

    recipes = SmallRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('__all__',)

    def get_recipes_count(self, obj: User) -> int:
        """Показывает общее количество рецептов у каждого автора.

        Args:
            obj (User): Запрошенный пользователь.

        Returns:
            int: Количество рецептов созданных запрошенным пользователем.
        """
        return obj.recipes.count()
