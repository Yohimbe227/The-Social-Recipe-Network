from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, F

from backend import settings


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=settings.AUTH_MAX_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='имя',
        max_length=settings.AUTH_MAX_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=settings.AUTH_MAX_LENGTH,
    )
    is_subscribed = models.BooleanField(blank=True, default=False)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Subscriptions(models.Model):

    author = models.ForeignKey(
        User,
        verbose_name='автор рецепта',
        related_name='subscribers',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='подписчики',
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='Вы уже подписались!',
            ),
            models.CheckConstraint(
                check=~Q(author=F('user')),
                name='Подписываться на себя? Не нужно!'
            )
        )

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'
