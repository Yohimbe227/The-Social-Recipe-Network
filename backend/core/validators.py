from string import hexdigits

from rest_framework.exceptions import ValidationError


def color_validator(color: str) -> str:
    """Проверяет - может ли значение быть шестнадцатеричным цветом.

    Args:
        color (str):
            Значение переданное для проверки.

    Raises:
        ValidationError:
            Переданное значение не корректной длины.
        ValidationError:
            Символы значения выходят за пределы 16-ричной системы.
    """

    color = color.strip(" #")
    if len(color) not in (3, 6):
        raise ValidationError(f"Код цвета {color} не правильной длины ({len(color)}).")
    if not set(color).issubset(hexdigits):
        raise ValidationError(f"{color} не шестнадцатиричное.")
    if len(color) == 3:
        return f"#{color[0] * 2}{color[1] * 2}{color[2] * 2}".upper()
    return "#" + color.upper()


def tags_exist_validator(tags_ids: list[int | str], Tag: 'Tag') -> None:
    """Проверяет наличие тэгов с указанными id.

    Args:
        tags_ids (list[int | str]): Список id.
        Tag (Tag): Модель тэгов во избежании цикличного импорта.

    Raises:
        ValidationError: Тэга с одним из указанных id не существует.
    """
    exists_tags = Tag.objects.filter(id__in=tags_ids)

    if len(exists_tags) != len(tags_ids):
        raise ValidationError('Указан несуществующий тэг')

def ingredients_validator(
    ingredients: list[dict[str, str | int]],
    Ingredient: 'Ingredient',
) -> dict[int, tuple['Ingredient', int]]:
    """Проверяет список ингридиентов.

    Args:
        ingredients (list[dict[str, str | int]]):
            Список ингридиентов.
            Example: [{'amount': '5', 'id': 2073},]
        Ingredient (Ingredient):
            Модель ингридиентов во избежании цикличного импорта.

    Raises:
        ValidationError: Ошибка в переданном списке ингридиентов.

    Returns:
        dict[int, tuple[Ingredient, int]]:
    """
    valid_ings = {}

    for ing in ingredients:
        if not (isinstance(ing['amount'], int) or ing['amount'].isdigit()):
            raise ValidationError('Неправильное количество ингидиента')

        amount = valid_ings.get(ing['id'], 0) + int(ing['amount'])
        if amount <= 0:
            raise ValidationError('Неправильное количество ингридиента')

        valid_ings[ing['id']] = amount

    if not valid_ings:
        raise ValidationError('Неправильные ингидиенты')

    db_ings = Ingredient.objects.filter(pk__in=valid_ings.keys())
    if not db_ings:
        raise ValidationError('Неправильные ингидиенты')

    for ing in db_ings:
        valid_ings[ing.pk] = (ing, valid_ings[ing.pk])

    return valid_ings
