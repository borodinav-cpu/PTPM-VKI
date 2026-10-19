# -*- coding: utf-8 -*-
"""
Запуск всех юнит-тестов проекта с сохранением протокола в файл.

Использование:
    python run_tests.py

Создаёт папку Logs/ и два файла:
    * Logs/unittest_results.log — протокол unittest (verbose: список тестов, статусы ok/FAIL, сводка);
    * Logs/test_logging.log     — события модуля logging во время тестов
                                  (валидация из validator.py вызывалась тестами).
Код возврата: 0 — все тесты пройдены, 1 — есть падения/ошибки
(удобно для CI или для проверки успешности в скриптах).
"""
import datetime
import io
import logging
import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "Logs")

sys.path.insert(0, BASE_DIR)


def main():
    os.makedirs(LOG_DIR, exist_ok=True)

    # Сквозное логирование во время тестов: консоль + файл.
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | [%(levelname)-7s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(LOG_DIR, "test_logging.log"), encoding="utf-8"),
        ],
    )
    logging.info("Запуск юнит-тестов проекта")

    # Протокол unittest собираем в буфер и дублируем в файл.
    buffer = io.StringIO()
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.join(BASE_DIR, "tests"), top_level_dir=BASE_DIR)
    runner = unittest.TextTestRunner(stream=buffer, verbosity=2)
    result = runner.run(suite)

    protocol = buffer.getvalue()
    header = (
        f"Протокол прогона unittest | {datetime.date.today().isoformat()}"
        f" | Всего: {result.testsRun} | Провалено: {len(result.failures)}"
        f" | Ошибок: {len(result.errors)}\n"
        + "=" * 78 + "\n"
    )
    with open(os.path.join(LOG_DIR, "unittest_results.log"), "w", encoding="utf-8") as f:
        f.write(header + protocol)

    sys.stdout.write(protocol)
    logging.info(
        "Итог: всего=%s, провалено=%s, ошибок=%s",
        result.testsRun,
        len(result.failures),
        len(result.errors),
    )
    print("\nПротокол тестов:   Logs/unittest_results.log")
    print("События логгера:   Logs/test_logging.log")
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
