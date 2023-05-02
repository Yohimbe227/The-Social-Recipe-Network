from django.http import HttpRequest, HttpResponse
from rest_framework import status
from rest_framework.decorators import parser_classes
from rest_framework.exceptions import MethodNotAllowed, ParseError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.viewsets import ModelViewSet

from recipes.models import Recipe
from recipes.serializers import RecipeSerializer


class RecipeView(ModelViewSet):
    parser_class = (FileUploadParser,)
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    ordering_fields = (
        'name',
    )
    serializer_class = RecipeSerializer

    def post(self, request, format=None):
        if 'file' not in request.data:
            raise ParseError("Empty content")

        f = request.data['file']

        Recipe.image.save(f.name, f, save=True)
        return Response(status=status.HTTP_201_CREATED)

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

