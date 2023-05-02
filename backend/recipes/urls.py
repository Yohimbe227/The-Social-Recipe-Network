from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import RecipeView

router = DefaultRouter()
router.register('recipes', RecipeView, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
