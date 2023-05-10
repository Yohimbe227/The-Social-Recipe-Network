import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from recipes.models import Recipe, Tag, Ingredient

User = get_user_model()


class SmallRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe.

    Уменьшенный набор полей для некоторых эндпоинтов.
    """
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


class TagSerializer(serializers.ModelSerializer):

    def validate_color(self, color: str) -> str:
        """Проверка формата цвета.

        Args:
            color: Цвет тэга.

        Returns:
            Цвет тэга (проверено).

        Raises:
             ValidationError: Введите корректный цвет!

        """
        if color[0] != '#' or len(color) != 7:
            raise serializers.ValidationError('This is not color in HEX format')
        return color

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit',
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            extension, img_in_str = data.split(';base64,')
            ext = extension.split('/')[-1]
            data = ContentFile(base64.b64decode(img_in_str),
                               name='temp.' + ext)

        return super().to_internal_value(data)


class TagWriteField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, value):
        return {
            'id': value.pk,
            'name': value.name,
            'color': value.color,
            'slug': value.slug
        }


class RecipeWriteSerializer(WritableNestedModelSerializer):
    tags = TagWriteField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientSerializer(
        many=True,
    )
    image = Base64ImageField(required=False, allow_null=True)

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


class RecipeReadSerializer(serializers.ModelSerializer):

    tags = TagSerializer(
        many=True,
        read_only=True,
    )

    ingredients = IngredientSerializer(
        many=True,
        read_only=True,
    )
    image = serializers.ImageField(required=True)
    author = UserSerializer()

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


class UserSerializer(ModelSerializer):
    """Сериализатор для использования с моделью User.
    """
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
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj: User) -> bool:
        """Проверка подписки пользователей.

        Определяет - подписан ли текущий пользователь
        на просматриваемого пользователя.

        Args:
            obj (User): Пользователь, на которого проверяется подписка.

        Returns:
            bool: True, если подписка есть. Во всех остальных случаях False.
        """
        user = self.context.get('request').user

        if user.is_anonymous or (user == obj):
            return False

        return user.subscriptions.filter(author=obj).exists()

    def create(self, validated_data: dict) -> User:
        """ Создаёт нового пользователя с запрошенными полями.

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


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор вывода авторов на которых подписан текущий пользователь.
    """
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
        read_only_fields = '__all__',

    def get_is_subscribed(*args) -> bool:
        """Проверка подписки пользователей.

        Переопределённый метод родительского класса для уменьшения нагрузки,
        так как в текущей реализации всегда вернёт `True`.

        Returns:
            bool: True
        """
        return True

    def get_recipes_count(self, obj: User) -> int:
        """ Показывает общее количество рецептов у каждого автора.

        Args:
            obj (User): Запрошенный пользователь.

        Returns:
            int: Количество рецептов созданных запрошенным пользователем.
        """
        return obj.recipes.count()
