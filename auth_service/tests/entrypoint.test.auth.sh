#!/bin/bash
set -e

# Ждём, пока Postgres поднимется
echo "⏳ Waiting for Postgres..."
until pg_isready -h test_postgres -p 5432 -U "$TEST_DB_USER"; do
  sleep 1
done
echo "✅ Postgres is up"

# Применяем миграции
echo "🚀 Running migrations..."
alembic -c alembic_test.ini upgrade head

# (опционально) Чистим БД перед тестами
# psql -h test_postgres -U postgres -d test_auth_db -c "TRUNCATE TABLE users CASCADE;"

echo "👑 Ensuring superuser exists..."
python create_superuser.py

# Запускаем тесты
echo "🧪 Running pytest..."
pytest -vv --disable-warnings --maxfail=1
