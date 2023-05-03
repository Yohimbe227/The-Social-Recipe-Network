from django.contrib.auth import get_user_model
from django.db import models

from backend.settings import NAME_MAX_LENGTH, UNIT_MAX_LENGTH

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    amount = models.PositiveIntegerField()
    measurement_unit = models.CharField(max_length=UNIT_MAX_LENGTH)

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

    def __str__(self) -> str:
        return self.name


def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class Recipe(models.Model):
    text = models.TextField(
        max_length=2000,
        verbose_name='Описание рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="автор",
        null=True,
    )
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='title',
        verbose_name='Название ингридиента',
    )
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    is_favorited = models.BooleanField()
    is_in_shopping_cart = models.BooleanField()
    tags = models.ManyToManyField(
        Tag,
        through='TagReceipt',
    )
    cooking_time = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self) -> str:
        return self.name


class TagReceipt(models.Model):

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


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
        null=True,
    )

    class Meta:
        unique_together = (
            'user',
            'author',
        )

    def __str__(self) -> str:
        return f'Подписался {self.user} на {self.author}'
