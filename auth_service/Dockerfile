FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc libpq-dev netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONPATH=/app/src

# Скопируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем весь проект
COPY . .

# Делаем entrypoint исполняемым (после копирования!)
RUN chmod +x /app/entrypoint.sh

# Задаём entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
