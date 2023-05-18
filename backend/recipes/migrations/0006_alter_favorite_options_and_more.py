# Generated by Django 4.2 on 2023-05-16 07:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0005_rename_ingredient_amountingredient_ingredients"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="favorite",
            options={
                "verbose_name": "Избранный рецепт",
                "verbose_name_plural": "Избранные рецепты",
            },
        ),
        migrations.AlterField(
            model_name="amountingredient",
            name="ingredients",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipe",
                to="recipes.ingredient",
                verbose_name="Связанные ингредиенты",
            ),
        ),
        migrations.AlterField(
            model_name="amountingredient",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredient",
                to="recipes.recipe",
                verbose_name="В каких рецептах",
            ),
        ),
    ]