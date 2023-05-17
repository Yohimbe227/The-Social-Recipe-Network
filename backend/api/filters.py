from rest_framework import filters


class IngredientFilterBackend(filters.BaseFilterBackend):
    """Фильтр ингридиентов по имени."""

    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name')

        if name:
            return queryset.filter(
                name__icontains=request.query_params.get('name'),
            )
        return queryset
