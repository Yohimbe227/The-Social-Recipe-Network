from django.http import HttpRequest, HttpResponse
from rest_framework import status
from rest_framework.decorators import parser_classes
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Recipe, Tag, User
from recipes.pagination import RecipePagination
from recipes.serializers import RecipeReadSerializer, RecipeWriteSerializer, \
    TagSerializer, CurrentUserSerializer


class RecipeView(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination
    ordering_fields = (
        'name',
    )

    def update(self, *args: list, **kwargs: dict) -> Response:
        """
        Deny access to the PUT method .

        Args:
            *args: not used.
            **kwargs: not used.

        Returns:
            MethodNotAllowed exception.

        """
        raise MethodNotAllowed('PUT', detail='Use PATCH')

    def partial_update(
        self,
        request: HttpRequest,
        *args: list,
        **kwargs: dict,
    ) -> Response:
        """Override Partial Update Code if desired.

        Args:
            request: HTTPRequest.
            *args: not used.
            **kwargs: not used.

        Returns:
            Updated output.

        """
        return super().update(request, *args, **kwargs, partial=True)

    def get_serializer_class(self) -> [
        RecipeReadSerializer, RecipeWriteSerializer,
    ]:
        """Call the desired serializer depending on the type of query.

        Returns:
            Desired serializer.
        """
        if self.action in (
            'list',
            'retrieve',
        ):
            return RecipeReadSerializer
        return RecipeWriteSerializer


class TagView(ModelViewSet):
    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer


class CurrentUserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = CurrentUserSerializer
