from string import hexdigits

from rest_framework.exceptions import ValidationError


def color_validator(color: str) -> str:
    """Проверяет - может ли значение быть шестнадцатеричным цветом.

    Args:
        color:
            Значение переданное для проверки.

    Raises:
        ValidationError:
            Переданное значение не корректной длины.
        ValidationError:
            Символы значения выходят за пределы 16-ричной системы.

    """
    color = color.strip(' #')
    if len(color) != 6:
        raise ValidationError(
            f'Код цвета {color} не правильной длины.',
        )
    if not set(color).issubset(hexdigits):
        raise ValidationError(f'{color} не шестнадцатиричное.')

    return '#' + color.upper()
