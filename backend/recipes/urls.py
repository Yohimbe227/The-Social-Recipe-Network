from api.views import RecipeView, TagView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("recipes", RecipeView, basename="recipes")
router.register("tags", TagView, basename="recipes")


urlpatterns = [
    path("", include(router.urls)),
]
