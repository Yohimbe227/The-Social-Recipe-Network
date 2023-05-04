from djoser.views import UserViewSet

from rest_framework_simplejwt.views import TokenObtainPairView


from users.models import User
from users.serializers import CustomTokenObtainPairSerializer, \
    UserSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
