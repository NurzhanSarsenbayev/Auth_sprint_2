#!/bin/sh
set -eu

export PGPASSWORD=$POSTGRES_PASSWORD

echo "⏳ Ensuring database $POSTGRES_DB exists..."
until psql -h $POSTGRES_HOST -U $POSTGRES_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" | grep -q 1; do
  echo "⏳ Waiting for database creation..."
  sleep 2
  psql -h $POSTGRES_HOST -U $POSTGRES_USER -c "CREATE DATABASE $POSTGRES_DB" || true
done
echo "✅ Database $POSTGRES_DB is ready"

# создаём базу если её нет
psql -h $POSTGRES_HOST -U $POSTGRES_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" | grep -q 1 || \
    psql -h $POSTGRES_HOST -U $POSTGRES_USER -c "CREATE DATABASE $POSTGRES_DB"

echo "⏳ Waiting for Redis..."
until nc -z "$REDIS_HOST" "$REDIS_PORT"; do
  sleep 1
done
echo "✅ Redis is up"

python manage.py migrate --noinput

# опционально: создадим локального суперюзера (на случай фейла SSO)
python manage.py ensure_local_superuser || true

python manage.py collectstatic --noinput

# gunicorn для прод-подобного запуска
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
