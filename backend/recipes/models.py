from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint, PositiveSmallIntegerField
from rest_framework.fields import DateTimeField

from backend.settings import NAME_MAX_LENGTH, UNIT_MAX_LENGTH
from core.validators import color_validator

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True)
    amount = models.PositiveIntegerField()
    measurement_unit = models.CharField(
        max_length=UNIT_MAX_LENGTH,
        default='г'
    )

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'

    def __str__(self) -> str:
        return self.name


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


def upload_to(instance, filename):
    return f'images/{filename}'


class Recipe(models.Model):
    text = models.TextField(
        max_length=2000,
        verbose_name='Описание рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="автор",
        related_name='recipes',
        null=True,
    )
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredient',
        verbose_name='название ингридиента',
    )
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    is_favorited = models.BooleanField()
    is_in_shopping_cart = models.BooleanField()
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
    )
    cooking_time = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self) -> str:
        return self.name


class TagRecipe(models.Model):

    tags = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    receipt = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    verbose_name = 'тэг'


class IngredientRecipe(models.Model):
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    receipt = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    verbose_name = 'ингридиенты'


class AmountIngredient(models.Model):
    """Количество ингридиентов в блюде.

    Модель связывает Recipe и Ingredient с указанием количества ингридиента.

    Attributes:
        recipe(int):
            Связаный рецепт. Связь через ForeignKey.
        ingredients(int):
            Связаный ингридиент. Связь через ForeignKey.
        amount(int):
            Количиства ингридиента в рецепте. Установлены ограничения
            по минимальному и максимальному значениям.

    """
    recipe = models.ForeignKey(
        verbose_name='В каких рецептах',
        related_name='ingredient',
        to=Recipe,
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        to=Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(
            MinValueValidator(
                1,
                'Нужно хоть какое-то количество.',
            ),
            MaxValueValidator(
                100,
                'Слишком много!',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe', )
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredients', ),
                name='\n%(app_label)s_%(class)s ingredient alredy added\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class Favorites(models.Model):
    """Избранные рецепты.

    Модель связывает Recipe и  User.

    Attributes:
        recipe(int):
            Связаный рецепт. Связь через ForeignKey.
        user(int):
            Связаный пользователь. Связь через ForeignKey.
        date_added(datetime):
            Дата дбавления рецепта в избранное.
    """
    recipe = models.ForeignKey(
        verbose_name='Понравившиеся рецепты',
        related_name='in_favorites',
        to=Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='favorites',
        to=User,
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user', ),
                name='\n%(app_label)s_%(class)s recipe is favorite alredy\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'


class Carts(models.Model):
    """Рецепты в корзине покупок.

    Модель связывает Recipe и  User.

    Attributes:
        recipe(int):
            Связаный рецепт. Связь через ForeignKey.
        user(int):
            Связаный пользователь. Связь через ForeignKey.
        date_added(datetime):
            Дата добавления рецепта в корзину.
    """
    recipe = models.ForeignKey(
        verbose_name='Рецепты в списке покупок',
        related_name='in_carts',
        to=Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name='Владелец списка',
        related_name='carts',
        to=User,
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user', ),
                name='%(app_label)s_%(class)s recipe is cart alredy',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'
