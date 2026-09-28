import re
import hashlib
import logging

BLACKLIST = {"admin", "root", "user", "test", "qwerty", "administrator",
             "moderator", "guest", "support", "system"}

PHONE_RE = re.compile(r"^\+\d{1,3}-\d{3}-\d{3}-\d{4}$")
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
LOGIN_RE = re.compile(r"^[A-Za-z0-9_]{5,}$")
PASSWORD_RE = re.compile(r"^[А-Яа-яЁё0-9!@#$%^&*()_\-+=.,:;?/\\|{}\[\]<>~`\"']+$")


def mask_password(password: str) -> str:
    """Маскирует пароль: одинаковые пароли → одинаковый хеш, разные → разные."""
    if not password:
        return "[EMPTY]"
    return "SHA256:" + hashlib.sha256(password.encode("utf-8")).hexdigest()[:16]


def validate_login(login: str):
    if not login:
        return "Логин не может быть пустым"

    if login.startswith("+"):
        if not PHONE_RE.match(login):
            return "Неверный формат телефона (ожидается +x-xxx-xxx-xxxx)"
        return None

    if "@" in login:
        if not EMAIL_RE.match(login):
            return "Неверный формат email"
        return None

    if len(login) < 5:
        return "Логин должен содержать минимум 5 символов"
    if not LOGIN_RE.match(login):
        return "Логин может содержать только латиницу, цифры и _"
    if login.lower() in BLACKLIST:
        return "Логин находится в чёрном списке"
    return None


def validate_password(password: str, confirm: str):
    if len(password) < 7:
        return "Пароль должен содержать минимум 7 символов"
    if not PASSWORD_RE.match(password):
        return "Пароль может содержать только кириллицу, цифры и спецсимволы"
    if not re.search(r"[А-ЯЁ]", password):
        return "Пароль должен содержать хотя бы одну заглавную букву"
    if not re.search(r"[а-яё]", password):
        return "Пароль должен содержать хотя бы одну строчную букву"
    if not re.search(r"\d", password):
        return "Пароль должен содержать хотя бы одну цифру"
    if not re.search(r"[!@#$%^&*()_\-+=.,:;?/\\|{}\[\]<>~`\"']", password):
        return "Пароль должен содержать хотя бы один спецсимвол"
    if password != confirm:
        return "Пароль и подтверждение не совпадают"
    return None


def validate_registration(login: str, password: str, confirm: str):
    """Возвращает (успех: bool, сообщение: str)."""
    try:
        logging.debug(f"Валидация: логин='{login}', пароль={mask_password(password)}")

        err = validate_login(login)
        if err:
            logging.error(f"Ошибка валидации логина: {err}")
            return False, err

        err = validate_password(password, confirm)
        if err:
            logging.error(f"Ошибка валидации пароля: {err}")
            return False, err

        logging.info("Валидация пройдена успешно")
        return True, ""

    except Exception:
        logging.exception("Непредвиденная ошибка при валидации")
        return False, "Внутренняя ошибка валидации"