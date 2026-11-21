# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.13.8 AS uv

FROM python:3.14-slim AS builder
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

FROM python:3.14-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"
RUN groupadd --gid 10001 wish \
    && useradd --uid 10001 --gid wish --no-create-home wish \
    && mkdir -p /var/lib/wish/data /var/lib/wish/media /var/lib/wish/static \
    && chown -R wish:wish /var/lib/wish
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src ./src
COPY deploy ./deploy
USER 10001:10001
EXPOSE 8000
CMD ["gunicorn", "--config", "deploy/gunicorn_config.py", "wish_list_config.wsgi:application"]
