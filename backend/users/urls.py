from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


from users.serializers import EmailTokenObtainPairView
from users.views import CustomUserViewSet

router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/token/login/', EmailTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('auth/token/logout/', TokenRefreshView.as_view(),
         name='token_delete'),
    path('', include(router.urls),
         name='users'),
]
