# Wish List

## Требования

- [uv](https://docs.astral.sh/uv/)

## Запуск

```bash
uv sync
uv run pre-commit install
cp .env.example .env # Надо сгенерировать SECRET_KEY
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Проверки

```bash
uv run pre-commit run --all-files
uv run mypy .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run pytest --cov
```
