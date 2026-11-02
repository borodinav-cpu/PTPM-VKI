# PTPM-VKI

Здесь будут все лабы по тестированию.
Также в рид ми будет вся информация по заданию лабораторной работы, а ветки нужны для разделения лаб в репозитории студента.

## Срезовая работа: модуль валидации пароля

```text
.
├── src/
│   ├── __init__.py
│   └── password_validator.py
└── tests/
    ├── __init__.py
    └── test_password_validator.py
```

### Запуск тестов

```bash
python -m unittest discover -s tests -v
```

### Контроль покрытия

```bash
python -m coverage run --source=src -m unittest discover -s tests -v
python -m coverage report -m
```
