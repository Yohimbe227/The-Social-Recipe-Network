from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import (
    CheckConstraint,
    PositiveSmallIntegerField,
    Q,
    UniqueConstraint,
)
from PIL import Image

from backend.settings import NAME_MAX_LENGTH
from core.constants import Additional, Limits
from core.validators import color_validator

User = get_user_model()


class Ingredient(models.Model):
    """ингредиенты для рецепта.

    Связано с моделью Recipe через М2М (AmountIngredient).

    Attributes:
        name:
            Название ингредиента.
            Установлены ограничения по длине и уникальности.
        measurement_unit:
            Единицы измерения ингредентов (граммы, штуки, литры и т.п.).
            Установлены ограничения по длине.

    """

    name = models.CharField(
        verbose_name='ингредиент',
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD,
    )
    measurement_unit = models.CharField(
        verbose_name='единицы измерения',
        max_length=24,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_for_ingredient',
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='%(app_label)s_%(class)s_name пусто',
            ),
            CheckConstraint(
                check=Q(measurement_unit__length__gt=0),
                name='%(app_label)s_%(class)s_measurement_unit пусто',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'

    def clean(self) -> None:
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        super().clean()


class Tag(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    color = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'

    def clean(self) -> None:
        self.name = self.name.strip().lower()
        self.slug = self.slug.strip().lower()
        self.color = color_validator(self.color)
        return super().clean()

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Модель для рецептов."""

    name = models.CharField(
        verbose_name='название блюда',
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD,
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор рецепта',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='тэг',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ингредиенты блюда',
        related_name='recipes',
        through='AmountIngredient',
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
        editable=False,
    )
    image = models.ImageField(
        verbose_name='изображение блюда',
        upload_to='',
    )
    text = models.TextField(
        verbose_name='описание блюда',
        max_length=Limits.MAX_LEN_RECIPES_TEXTFIELD,
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='время приготовления',
        default=0,
        validators=(
            MinValueValidator(
                Limits.MIN_COOKING_TIME,
                'Введите корректное время!',
            ),
            MaxValueValidator(
                Limits.MAX_COOKING_TIME,
                'Слишком долго ждать...',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='%(app_label)s_%(class)s_name is empty',
            ),
        )

    def __str__(self) -> str:
        if self.author:
            return f'{self.name}. Автор: {self.author.username}'
        return f'{self.name}. Автор был удален'

    def clean(self) -> None:
        self.name = self.name.capitalize()
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image = image.resize(Additional.RECIPE_IMAGE_SIZE)
        image.save(self.image.path)


class AmountIngredient(models.Model):
    """Количество ингредиентов в блюде.

    Модель связывает Recipe и Ingredient с указанием количества ингредиента.

    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В каких рецептах',
        related_name='ingredientrecipes',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        related_name='ingredientrecipes',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
        validators=(
            MinValueValidator(
                1,
                'Добавьте что-нибудь!',
            ),
        ),
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)
        constraints = (
            UniqueConstraint(
                fields=(
                    'recipe',
                    'ingredients',
                ),
                name='%(app_label)s_%(class)s ингредиенты добавлены',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class Favorite(models.Model):
    """Избранные рецепты.

    Модель связывает Recipe и  User.

    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='понравившиеся рецепты',
        related_name='in_favorites',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='дата добавления',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'избранные рецепты'
        constraints = (
            UniqueConstraint(
                fields=(
                    'recipe',
                    'user',
                ),
                name='%(app_label)s_%(class)s рецепт уже в избранном',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'


class Cart(models.Model):
    """Рецепты в корзине покупок.

    Модель связывает Recipe и  User.

    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепты в списке покупок',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='владелец списка',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'рецепт в списке покупок'
        verbose_name_plural = 'рецепты в списке покупок'
        constraints = (
            UniqueConstraint(
                fields=(
                    'recipe',
                    'user',
                ),
                name='%(app_label)s_%(class)s рецепт уже в списке',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} добавил в корзину {self.recipe}'
