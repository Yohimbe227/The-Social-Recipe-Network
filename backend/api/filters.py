from rest_framework import filters


class IngredientFilterBackend(filters.BaseFilterBackend):
    """Фильтр ингридиентов по имени."""

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            name__icontains=request.query_params.get('name'),
        )
