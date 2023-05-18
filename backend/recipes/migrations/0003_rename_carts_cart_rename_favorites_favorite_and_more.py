# Generated by Django 4.2 on 2023-05-15 09:45

import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipes", "0002_alter_ingredient_options_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Carts",
            new_name="Cart",
        ),
        migrations.RenameModel(
            old_name="Favorites",
            new_name="Favorite",
        ),
        migrations.AlterModelOptions(
            name="favorite",
            options={
                "verbose_name": "избранный рецепт",
                "verbose_name_plural": "избранные рецепты",
            },
        ),
        migrations.RemoveConstraint(
            model_name="amountingredient",
            name="recipes_amountingredient ingredient alredy added",
        ),
        migrations.RemoveConstraint(
            model_name="cart",
            name="recipes_carts рецепт уже в списке",
        ),
        migrations.RemoveConstraint(
            model_name="favorite",
            name="recipes_favorites recipe is favorite alredy",
        ),
        migrations.AlterField(
            model_name="amountingredient",
            name="amount",
            field=models.PositiveSmallIntegerField(
                default=1,
                validators=[
                    django.core.validators.MinValueValidator(
                        1, "Добавьте что-нибудь!"
                    )
                ],
                verbose_name="Количество",
            ),
        ),
        migrations.AddConstraint(
            model_name="amountingredient",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredients"),
                name="recipes_amountingredient ингредиенты добавлены",
            ),
        ),
        migrations.AddConstraint(
            model_name="cart",
            constraint=models.UniqueConstraint(
                fields=("recipe", "user"),
                name="recipes_cart рецепт уже в списке",
            ),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("recipe", "user"),
                name="recipes_favorite рецепт уже в избранном",
            ),
        ),
    ]
