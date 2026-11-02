"""Модуль валидации пароля на соответствие политикам безопасности."""

SPECIAL_CHARS = frozenset("!@#$%^&*")
MIN_LENGTH = 8
MAX_LENGTH = 20


def validate_password(password: str) -> bool:
    """
    Выполняет валидацию строки пароля на соответствие политикам безопасности.

    :param password: Проверяемый пароль
    :return: True, если пароль удовлетворяет всем условиям, иначе False
    :raises TypeError: Если входной параметр не является строкой
    :raises ValueError: Если входная строка содержит символы пробела
    """
    if not isinstance(password, str):
        raise TypeError("Пароль должен быть строкой")

    if " " in password:
        raise ValueError("Пароль не должен содержать пробелы")

    if not MIN_LENGTH <= len(password) <= MAX_LENGTH:
        return False

    if not any(char.isupper() for char in password):
        return False

    if not any(char.islower() for char in password):
        return False

    if not any(char.isdigit() for char in password):
        return False

    if not any(char in SPECIAL_CHARS for char in password):
        return False

    return True
