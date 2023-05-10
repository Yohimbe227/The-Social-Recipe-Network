from api.views import (RecipeView,
                       TagView, UserViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagView, 'tags')
# router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeView, 'recipes')
router.register('users', UserViewSet, 'users')

urlpatterns = (
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)
