import base64

from django.core.files.base import ContentFile
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from recipes.models import Recipe, Tag, Ingredient

from users.serializers import CustomUserSerializer


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
    author = CustomUserSerializer()

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
