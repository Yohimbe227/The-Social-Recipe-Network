# Generated by Django 4.2 on 2023-05-10 05:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0005_alter_ingredient_amount_alter_ingredient_name"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Follow",
        ),
    ]