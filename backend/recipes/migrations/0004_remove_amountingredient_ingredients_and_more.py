# Generated by Django 4.2 on 2023-05-15 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "recipes",
            "0003_rename_carts_cart_rename_favorites_favorite_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="amountingredient",
            name="ingredients",
        ),
        migrations.AddField(
            model_name="amountingredient",
            name="ingredient",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredientrecipes",
                to="recipes.ingredient",
                verbose_name="Связанные ингредиенты",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="amountingredient",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredientrecipes",
                to="recipes.recipe",
                verbose_name="В каких рецептах",
            ),
        ),
    ]