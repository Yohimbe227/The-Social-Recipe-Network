from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, F, CheckConstraint
from django.db.models.functions import Length

from backend import settings

models.CharField.register_lookup(Length)


class MyUser(AbstractUser):

    email = models.EmailField(
        verbose_name='адрес электронной почты',
        max_length=256,
        unique=True,
        # help_text=texsts.USERS_HELP_EMAIL,
    )
    username = models.CharField(
        verbose_name='юзернейм',
        max_length=256,
        unique=True,
        # help_text=texsts.USERS_HELP_UNAME,
        # validators=(
        #     MinLenValidator(
        #         min_len=3,
        #         field='username',
        #     ),
        # ),
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=256
        # help_text=texsts.USERS_HELP_FNAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=256,
        # help_text=texsts.USERS_HELP_FNAME,
        # validators=(OneOfTwoValidator(
        #     first_regex='[^а-яёА-ЯЁ -]+',
        #     second_regex='[^a-zA-Z -]+',
        #     field='Фамилия'),
        # ),
    )
    # password = models.CharField(
    #     verbose_name='Пароль',
    #     max_length=128,
    #     # help_text=texsts.USERS_HELP_FNAME,
    # )
    is_active = models.BooleanField(
        verbose_name='Активирован',
        default=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
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
        return f'{self.user.username} подписан на {self.author.username}'
