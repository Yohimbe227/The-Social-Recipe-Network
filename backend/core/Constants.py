"""Настройки параметров.
"""

# Размер сохраняемого изображения рецепта
RECIPE_IMAGE_SIZE = (500, 300)
# Поиск объектов только с переданным параметром.
# Например только в избранном: `is_favorited=1`
SYMBOL_TRUE_SEARCH = ('1', 'true')
# Поиск объектов не содержащих переданный параметр.
# Например только не избранное: `is_favorited=0`
SYMBOL_FALSE_SEARCH = ('0', 'false')
ADD_METHODS = ('GET', 'POST')
DEL_METHODS = ('DELETE',)
ACTION_METHODS = ('GET', 'POST', 'DELETE')
UPDATE_METHODS = ('PUT', 'PATCH')
