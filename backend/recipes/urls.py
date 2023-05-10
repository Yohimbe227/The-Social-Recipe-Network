from django.urls import path, include
from rest_framework.routers import DefaultRouter


from api.views import RecipeView, TagView

router = DefaultRouter()
router.register('recipes', RecipeView, basename='recipes')
router.register('tags', TagView, basename='recipes')


urlpatterns = [
                  path('', include(router.urls)),
              ]

