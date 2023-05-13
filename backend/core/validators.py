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
