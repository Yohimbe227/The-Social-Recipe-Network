import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Recipe, Tag, Ingredient, User
from recipes.validators import ColorValidate


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


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'id')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            extension, img_in_str = data.split(';base64,')
            ext = extension.split('/')[-1]
            data = ContentFile(base64.b64decode(img_in_str),
                               name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Tag.objects.all()
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'author',
            'image',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
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
    author = CurrentUserSerializer()

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
