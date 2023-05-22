from django_filters import ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet
from rest_framework import filters

from recipes.models import Tag


class IngredientFilterBackend(filters.BaseFilterBackend):
    """Фильтр ингредиентов по имени."""

    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name')

        if name:
            return queryset.filter(
                name__icontains=request.query_params.get('name'),
            )
        return queryset


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
