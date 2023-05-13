"""Дополнительные классы
для настройки основных классов приложения.
"""
from core.constants import Methods
from django.db.models import Model, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer


class AddDelView:
    """
    Добавляет во Viewset дополнительные методы.

    Содержит метод добавляющий/удаляющий объект связи
    Many-to-Many между моделями.
    Требует определения атрибута `add_serializer`.

    Example:
        class ExampleViewSet(ModelViewSet, AddDelViewMixin)
            ...
            add_serializer = ExamplSerializer

            def example_func(self, request, **kwargs):
                ...
                obj_id = ...
                return self.add_del_obj(obj_id, relation.M2M)
    """

    add_serializer: ModelSerializer | None = None

    def _add_del_obj(self, obj_id: int | str, m_to_m_model: Model, q: Q) -> Response:
        """Добавляет/удаляет связь `many to many`.

        Args:
            obj_id:
                `id` объекта, с которым требуется создать/удалить связь.
            m_to_m_model (Model):
                М2M модель управляющая требуемой связью.
            q:
                Условие фильтрации объектов.

        Returns:
            Responce: Статус подтверждающий/отклоняющий действие.

        """
        obj = get_object_or_404(self.queryset, id=obj_id)
        serializer: ModelSerializer = self.add_serializer(obj)
        m2m_obj = m_to_m_model.objects.filter(q & Q(user=self.request.user))

        if (self.request.method in Methods.ADD_METHODS) and not m2m_obj:
            # Table must have: | m2m.id | obj.id(FK) | user.id(FK) | ... |
            m_to_m_model(None, obj.id, self.request.user.id).save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if (self.request.method in Methods.DEL_METHODS) and m2m_obj:
            m2m_obj[0].delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'Вы не подписаны на {obj.username}!'},
            status=status.HTTP_400_BAD_REQUEST,
        )
