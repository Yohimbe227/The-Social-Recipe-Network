# from typing import Any
#
# from djoser.views import UserViewSet
# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.generics import get_object_or_404
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
#
# from users.models import User, Follow
# from users.serializers import CustomUserSerializer, FollowSerializer, \
#     FollowCreateSerializer
#
#
# class CustomUserViewSet(UserViewSet):
#     queryset = User.objects.all()
#     serializer_class = CustomUserSerializer
#
#     @action(detail=True, methods=['POST'], url_path='subscribe')
#     def user_subscribe_add(self, request, id):
#         user = request.user
#         # print(user)
#         following = User.objects.filter(pk=id)
#         # print(following)
#         # following = get_object_or_404(CustomUser, pk=id)
#         serializer = FollowCreateSerializer(
#             data={'user': user.id, 'following': id},
#             context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         follow = get_object_or_404(Follow, user=user, following=following)
#         serializer = FollowSerializer(follow.author,
#                                       context={'request': request})
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     @action(detail=True, methods=['get'], url_path='subscribe')
#     def user_subscribe_add(self, request, id):
#         user = request.user
#         # print(user)
#         serializer = FollowSerializer(
#             data={'user': user.id, 'following': id},
#             context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         follow = get_object_or_404(Follow, user=user, following=following)
#         serializer = FollowSerializer(follow.author,
#                                       context={'request': request})
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# # class FollowViewSet(viewsets.ModelViewSet):
# #     queryset = Follow.objects.select_related('Follow')
# #     serializer_class = FollowSerializer
# #     # filter_backends = (filters.SearchFilter,)
# #     search_fields = ('following__username',)
# #     permission_classes = [AllowAny, ]
# #
# #     def get_queryset(self) -> None:
# #         """
# #         Переопределяем `queryset`.
# #
# #         Returns:
# #             Все объекты подписок текущего пользователя.
# #         """
# #         return self.request.user.follower
# #
# #     def perform_create(self, serializer: FollowSerializer) -> None:
# #         """
# #         В поле `following` записываем значение из json запроса.
# #
# #         Args:
# #             serializer: Сериализатор `FollowSerializer`.
# #         """
# #         serializer.save(
# #             user=self.request.user,
# #             following=get_object_or_404(
# #                 User,
# #                 username=serializer.initial_data.get('following'),
# #             ),
# #         )
# #
