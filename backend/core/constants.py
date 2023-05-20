"""Настройки параметров."""


class Additional:
    def __setattr__(self, name, value):
        del value
        raise AttributeError(f"can't reassign constant '{name}'")

    RECIPE_IMAGE_SIZE = 500, 300

    SYMBOL_TRUE_SEARCH = '1', 'true'

    SYMBOL_FALSE_SEARCH = '0', "false"


class Methods:
    def __setattr__(self, name: str, value: tuple) -> None:
        raise AttributeError(f"can't reassign constant '{name}'")

    GET_POST_METHODS = 'GET', 'POST'
    DEL_METHODS = ('DELETE',)
    GET_POST_DEL_METHODS = 'GET', 'POST', 'DELETE'


class Limits:
    def __setattr__(self, name: str, value: tuple) -> None:
        raise AttributeError(f"can't reassign constant '{name}'")

    # Максимальная длина email (User)
    MAX_LEN_EMAIL_FIELD = 256
    # Максимальная длина строковых полей моделей в приложении 'users'
    MAX_LEN_USERS_CHARFIELD = 32
    # Максимальная длина строковых полей моделей в приложении 'recipes'
    MAX_LEN_RECIPES_CHARFIELD = 64
    # Максимальная длина единицы измеренияs моделей в приложении 'recipes'
    MAX_LEN_MEASUREMENT = 256
    # Максимальная длина текстовых полей моделей в приложении 'recipes'
    MAX_LEN_RECIPES_TEXTFIELD = 5000
    # Минимальное время приготовления рецепта в минутах
    MIN_COOKING_TIME = 1
    # Максимальное время приготовления рецепта в минутах
    MAX_COOKING_TIME = 6000
    # Минимальное количество ингредиентов для рецепта
    MIN_AMOUNT_INGREDIENTS = 1
    # Максимальное количество ингредиентов для рецепта
    MAX_AMOUNT_INGREDIENTS = 32
