from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, F, Q
from django.db.models.functions import Length

models.CharField.register_lookup(Length)


class MyUser(AbstractUser):
    email = models.EmailField(
        verbose_name='адрес электронной почты',
        max_length=256,
        unique=True,
    )
    username = models.CharField(
        verbose_name='юзернейм',
        max_length=256,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=256,
    )
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=256,
    )

    is_active = models.BooleanField(
        verbose_name='активирован',
        default=True,
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)
        constraints = (
            CheckConstraint(
                check=Q(username__length__gte=3),
                name='username is too short',
            ),
        )

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Subscriptions(models.Model):
    author = models.ForeignKey(
        MyUser,
        verbose_name='автор рецепта',
        related_name='subscribers',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        MyUser,
        verbose_name='подписчики',
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='дата создания подписки',
        auto_now_add=True,
        editable=False,
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
                name='Подписываться на себя? Не нужно!',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username} подписан на {self.author.username}'
