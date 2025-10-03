FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    netcat-traditional \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.admin.txt /app/
RUN pip install --no-cache-dir -r requirements.admin.txt

# Сначала кладём код (можешь оставить как было)
COPY . /app/

# 🔑 Кладём entrypoint ВНЕ /app, чиним CRLF и даём +x
COPY entrypoint.admin.sh /usr/local/bin/admin-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/admin-entrypoint.sh && \
    chmod +x /usr/local/bin/admin-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/admin-entrypoint.sh"]
