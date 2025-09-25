#!/bin/sh
set -e

echo "⏳ Waiting for Elasticsearch..."
python3 functional/utils/wait_for_es.py

echo "⏳ Waiting for Redis..."
python3 functional/utils/wait_for_redis.py

echo "⏳ Waiting for API..."
python3 functional/utils/wait_for_api.py

# Запускаем CMD (pytest)
exec "$@"