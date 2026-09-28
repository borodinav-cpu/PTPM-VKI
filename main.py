import logging
import sys
import os

from validator import validate_registration

LOG_DIR = "Logs"
LOG_FILE = os.path.join(LOG_DIR, "file_txt.log")


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | [%(levelname)-7s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )


def main():
    setup_logging()
    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")

    login = input("Введите логин: ")
    password = input("Введите пароль: ")
    confirm = input("Повторите пароль: ")

    from validator import mask_password
    logging.info(
        f"Запрос на регистрацию. Логин='{login}', "
        f"пароль={mask_password(password)}, подтверждение={mask_password(confirm)}"
    )

    success, message = validate_registration(login, password, confirm)

    if success:
        logging.info(f"Результат: True. Сообщение: '{message}'")
    else:
        logging.warning(f"Результат: False. Сообщение: '{message}'")

    print(success)
    print(message)


if __name__ == "__main__":
    main()