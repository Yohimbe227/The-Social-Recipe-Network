# Generated by Django 4.2 on 2023-05-16 15:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        (
            "recipes",
            "0009_cart_rename_favorites_favorite_remove_carts_recipe_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="автор рецепта",
            ),
            preserve_default=False,
        ),
    ]
