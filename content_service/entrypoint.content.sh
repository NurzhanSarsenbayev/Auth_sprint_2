#!/bin/sh
set -eu

echo "⏳ Waiting for Redis..."
until nc -z "$REDIS_HOST" "$REDIS_PORT"; do
  sleep 1
done
echo "✅ Redis is up"

echo "⏳ Waiting for Elasticsearch..."
until nc -z "$ELASTIC_HOST" "$ELASTIC_PORT"; do
  sleep 1
done
echo "✅ Elasticsearch is up"

echo "🚀 Starting Content Service..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
