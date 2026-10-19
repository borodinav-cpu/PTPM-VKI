import os
import sys
import unittest

# Позволяем запускать тесты как из корня проекта, так и из PyCharm:
# добавляем каталог src/ в путь поиска модулей.
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
)

from validator import (
    validate_login,
    validate_password,
    validate_registration,
    mask_password,
)


class TestValidateLogin(unittest.TestCase):
    """Тесты для функции validate_login."""

    def test_empty_login_returns_error(self):
        """Пустой логин → ошибка 'не может быть пустым'."""
        self.assertEqual(validate_login(""), "Логин не может быть пустым")

    def test_none_login_returns_error(self):
        """None вместо логина → ошибка 'не может быть пустым'."""
        self.assertEqual(validate_login(None), "Логин не может быть пустым")

    def test_valid_phone(self):
        """Корректный телефон → None (успех)."""
        self.assertIsNone(validate_login("+7-999-123-4567"))

    def test_phone_with_two_digit_country_code(self):
        """Телефон с кодом страны из 2 цифр → None."""
        self.assertIsNone(validate_login("+49-123-456-7890"))

    def test_invalid_phone_wrong_separator(self):
        """Телефон с пробелами вместо дефисов → ошибка."""
        self.assertIsNotNone(validate_login("+7 999 123 4567"))

    def test_invalid_phone_too_short_last_group(self):
        """Телефон с последней группой из 3 цифр → ошибка."""
        self.assertIsNotNone(validate_login("+7-999-123-456"))

    def test_valid_email(self):
        """Корректный email → None."""
        self.assertIsNone(validate_login("user@mail.ru"))

    def test_valid_email_with_plus(self):
        """Email с плюсом в локальной части → None."""
        self.assertIsNone(validate_login("user+tag@mail.ru"))

    def test_invalid_email_no_at(self):
        """Email без @ → не email, идёт как логин."""
        # '@' отсутствует → пойдёт по ветке обычного логина
        # 'usermail.ru' содержит точку — не пройдёт LOGIN_RE
        self.assertIsNotNone(validate_login("usermail.ru"))

    def test_invalid_email_double_at(self):
        """Email с двумя @ → ошибка."""
        self.assertIsNotNone(validate_login("user@@mail.ru"))

    def test_login_too_short(self):
        """Логин короче 5 символов → ошибка про минимум 5."""
        self.assertEqual(
            validate_login("abc"),
            "Логин должен содержать минимум 5 символов",
        )

    def test_login_with_cyrillic(self):
        """Кириллица в логине → ошибка (только латиница)."""
        self.assertIsNotNone(validate_login("иван123"))

    def test_login_with_space(self):
        """Пробел внутри логина → ошибка."""
        self.assertIsNotNone(validate_login("ivan 123"))

    def test_login_with_dash(self):
        """Дефис в логине → ошибка (разрешены только буквы, цифры, _)."""
        self.assertIsNotNone(validate_login("ivan-123"))

    def test_login_in_blacklist(self):
        """Логин из чёрного списка → ошибка."""
        self.assertEqual(
            validate_login("admin"),
            "Логин находится в чёрном списке",
        )

    def test_login_in_blacklist_uppercase(self):
        """Логин из чёрного списка в верхнем регистре → ошибка."""
        self.assertEqual(
            validate_login("ADMIN"),
            "Логин находится в чёрном списке",
        )

    def test_valid_login(self):
        """Корректный логин → None."""
        self.assertIsNone(validate_login("ivan_123"))


class TestValidatePassword(unittest.TestCase):
    """Тесты для функции validate_password."""

    def test_password_too_short(self):
        """Пароль короче 7 символов → ошибка."""
        self.assertEqual(
            validate_password("Аб1!", "Аб1!"),
            "Пароль должен содержать минимум 7 символов",
        )

    def test_password_with_latin(self):
        """Латиница в пароле → ошибка."""
        self.assertIsNotNone(validate_password("Password1!", "Password1!"))

    def test_password_with_space(self):
        """Пробел в пароле → ошибка."""
        self.assertIsNotNone(validate_password("Пароль 1!", "Пароль 1!"))

    def test_password_no_uppercase(self):
        """Нет заглавной буквы → ошибка."""
        self.assertEqual(
            validate_password("пароль1!", "пароль1!"),
            "Пароль должен содержать хотя бы одну заглавную букву",
        )

    def test_password_no_lowercase(self):
        """Нет строчной буквы → ошибка."""
        self.assertEqual(
            validate_password("ПАРОЛЬ1!", "ПАРОЛЬ1!"),
            "Пароль должен содержать хотя бы одну строчную букву",
        )

    def test_password_no_digit(self):
        """Нет цифры → ошибка."""
        self.assertEqual(
            validate_password("Пароль!!", "Пароль!!"),
            "Пароль должен содержать хотя бы одну цифру",
        )

    def test_password_no_special(self):
        """Нет спецсимвола → ошибка."""
        self.assertEqual(
            validate_password("Пароль12", "Пароль12"),
            "Пароль должен содержать хотя бы один спецсимвол",
        )

    def test_password_mismatch(self):
        """Пароль и подтверждение не совпадают → ошибка."""
        self.assertEqual(
            validate_password("Пароль1!", "Пароль2!"),
            "Пароль и подтверждение не совпадают",
        )

    def test_valid_password(self):
        """Корректный пароль → None."""
        self.assertIsNone(validate_password("Пароль1!", "Пароль1!"))

    def test_password_with_yo(self):
        """Пароль с буквой Ё → должен пройти."""
        self.assertIsNone(validate_password("Ёжик123!", "Ёжик123!"))


class TestValidateRegistration(unittest.TestCase):
    """Тесты для функции validate_registration."""

    def test_success(self):
        """Полностью корректные данные → True, пустое сообщение."""
        success, message = validate_registration(
            "ivan_123", "Пароль1!", "Пароль1!"
        )
        self.assertTrue(success)
        self.assertEqual(message, "")

    def test_bad_login(self):
        """Плохой логин → False, сообщение об ошибке."""
        success, message = validate_registration(
            "ab", "Пароль1!", "Пароль1!"
        )
        self.assertFalse(success)
        self.assertIn("минимум 5", message)

    def test_bad_password(self):
        """Плохой пароль → False."""
        success, message = validate_registration(
            "ivan_123", "abc", "abc"
        )
        self.assertFalse(success)
        self.assertIn("минимум 7", message)

    def test_mismatch(self):
        """Пароли не совпадают → False."""
        success, message = validate_registration(
            "ivan_123", "Пароль1!", "Пароль2!"
        )
        self.assertFalse(success)
        self.assertIn("не совпадают", message)

    def test_blacklist_login(self):
        """Логин из чёрного списка → False."""
        success, message = validate_registration(
            "admin", "Пароль1!", "Пароль1!"
        )
        self.assertFalse(success)
        self.assertIn("чёрном списке", message)


class TestMaskPassword(unittest.TestCase):
    """Тесты для функции mask_password."""

    def test_same_passwords_same_hash(self):
        """Одинаковые пароли → одинаковый хеш."""
        self.assertEqual(mask_password("Пароль1!"), mask_password("Пароль1!"))

    def test_different_passwords_different_hash(self):
        """Разные пароли → разный хеш."""
        self.assertNotEqual(mask_password("Пароль1!"), mask_password("Пароль2!"))

    def test_empty_password(self):
        """Пустой пароль → [EMPTY]."""
        self.assertEqual(mask_password(""), "[EMPTY]")

    def test_hash_does_not_contain_plaintext(self):
        """В хеше нет самого пароля."""
        self.assertNotIn("Пароль1!", mask_password("Пароль1!"))

    def test_hash_has_prefix(self):
        """Хеш начинается с 'SHA256:'."""
        self.assertTrue(mask_password("Пароль1!").startswith("SHA256:"))


if __name__ == "__main__":
    unittest.main()