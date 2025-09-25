#!/bin/bash
set -euo pipefail

echo "⏳ Waiting for Postgres..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "✅ Postgres is up"

echo "⏳ Waiting for Redis..."
until nc -z "$REDIS_HOST" "$REDIS_PORT"; do
  sleep 1
done
echo "✅ Redis is up"

echo "🚀 Running migrations..."
alembic upgrade head

echo "🌱 Seeding default roles..."
python seed_roles.py

echo "👑 Ensuring superuser exists..."
python create_superuser.py

echo "🚀 Starting app..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
