from django.contrib.auth import get_user_model
from django.db import models

from backend.backend.settings import NAME_MAX_LENGTH, UNIT_MAX_LENGTH

User = get_user_model()


class Ingredients(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=UNIT_MAX_LENGTH)
    duration = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'


class Tag(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    color = models.CharField(unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'


class Receipt(models.Model):
    description = models.TextField(
        max_length=2000,
        verbose_name='Описание рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    image = models.ImageField('картинка', upload_to='receipts/media',)

    ingredients = models.ManyToManyField(
        Ingredients,
        on_delete=models.SET_NULL,
        related_name='title',
        verbose_name='Название ингридиента',
    )
    name = models.CharField(max_length=NAME_MAX_LENGTH)

    tag = models.ManyToManyField(
        Tag,
        through='TagReceipt',
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'


class TagReceipt(models.Model):

    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
    )
    verbose_name = 'тэг'


class IngredientsReceipt(models.Model):
    ingredients = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
    )
    verbose_name = 'ингридиенты'
