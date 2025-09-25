FROM python:3.11-slim

WORKDIR /app

# Ставим системные пакеты для curl (для healthcheck)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Копируем requirements для тестов
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники тестов
COPY functional ./functional

# Копируем entrypoint
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["pytest --maxfail=0 --disable-warnings", "-v", "functional/tests"]