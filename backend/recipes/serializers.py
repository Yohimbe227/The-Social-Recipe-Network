from rest_framework import serializers

from recipes.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
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
            'slug',
            'quantity',
            'units',
            'duration',
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Tag.objects.all()
    )
    ingredients = serializers.RelatedField(
        many=True,
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'description',
            'author',
            'image',
            'ingredients',
            'tags'
        )
