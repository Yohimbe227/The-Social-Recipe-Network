from django.contrib.auth.models import AbstractUser
from django.db import models

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
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
