from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import RecipeView, TagView, CurrentUserViewSet

router = DefaultRouter()
router.register('recipes', RecipeView, basename='recipes')
router.register('tags', TagView, basename='recipes')
router.register('users', CurrentUserViewSet, basename='users')

urlpatterns = [
    # path('users/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
