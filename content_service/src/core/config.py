import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Название проекта (Swagger, логирование)
    project_name: str = Field(default="movies", env="PROJECT_NAME")

    # Redis
    redis_host: str = Field(default="127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")

    # Elasticsearch
    elastic_host: str = Field(default="127.0.0.1", env="ELASTIC_HOST")
    elastic_port: int = Field(default=9200, env="ELASTIC_PORT")

    # Auth
    auth_url: str = Field(default="http://auth_service:8000/api/v1/auth", env="AUTH_URL")

    # Тестовый режим
    testing: bool = Field(default=False, env="TESTING")

    # --- OpenTelemetry ---
    enable_tracer: bool = Field(default=True, env="ENABLE_TRACER")
    otel_service_name: str = Field(default="content_service", env="OTEL_SERVICE_NAME")
    otel_exporter_otlp_endpoint: str = Field(
        default="http://jaeger:4318/v1/traces", env="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    otel_sampling_ratio: float = Field(default=1.0, env="OTEL_SAMPLING_RATIO")
    environment: str = Field(default="dev", env="ENVIRONMENT")


class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Инициализируем конфиг (один раз)
settings = Settings()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
