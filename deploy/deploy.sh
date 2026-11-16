#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
env_file=${DEPLOY_ENV_FILE:-.env.production}

compose() {
    docker compose --env-file "$env_file" "$@"
}

compose config --quiet
compose build --pull web
compose pull caddy
compose run --rm --no-deps web python manage.py check --deploy --fail-level ERROR
compose run --rm --no-deps caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile

# Small single-server deployment: stop writes while changing the SQLite schema.
compose stop web
compose run --rm --no-deps web python manage.py migrate --noinput
compose run --rm --no-deps web python manage.py collectstatic --noinput
compose up -d --wait --wait-timeout 120
compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
compose ps
