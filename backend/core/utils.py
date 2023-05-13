from recipes.models import AmountIngredient, Ingredient, Recipe


def recipe_ingredients_set(
    recipe: Recipe, ingredients: dict[int, tuple['Ingredient', int]],
) -> None:
    """Записывает ингредиенты вложенные в рецепт.

    Создаёт объект AmountIngredient связывающий объекты Recipe и
    Ingredient с указанием количества `amount` конкретного ингридиента.

    Args:
        recipe:
            Рецепт, в который нужно добавить игридиенты.
        ingredients:
            Список ингридентов и их количества.

    """
    objs = []

    for ingredient, amount in ingredients.values():
        objs.append(
            AmountIngredient(
                recipe=recipe, ingredients=ingredient, amount=amount,
            ),
        )

    AmountIngredient.objects.bulk_create(objs)
