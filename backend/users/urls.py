from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# router.register('subscriptions', FollowViewSet)

urlpatterns = [
    # path('users/', include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include("djoser.urls")),
]
