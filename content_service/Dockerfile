FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# requirements.txt лежит в content_service/
COPY requirements.content.txt .
RUN pip install --no-cache-dir -r requirements.content.txt

# src и entrypoint.sh тоже в content_service/
COPY src ./src
COPY entrypoint.content.sh ./entrypoint.content.sh
RUN chmod +x ./entrypoint.content.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.content.sh"]
