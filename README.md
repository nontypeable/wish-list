# Wish List

## Требования

- [uv](https://docs.astral.sh/uv/)

## Структура

```text
src/                 # Django-приложения, manage.py, шаблоны и статика
tests/               # Тесты
deploy/              # Скрипты и настройки деплоя
```

## Запуск

```bash
uv sync
uv run pre-commit install
cp .env.example .env # Надо сгенерировать SECRET_KEY
uv run python src/manage.py migrate
uv run python src/manage.py createsuperuser
uv run python src/manage.py runserver
```

## Проверки

```bash
uv run pre-commit run --all-files
uv run mypy .
uv run python src/manage.py check
uv run python src/manage.py makemigrations --check --dry-run
uv run pytest --cov
```
