from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional

class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    jwt_algorithm: str
    jwt_private_key_path: str
    jwt_public_key_path: str

    @property
    def jwt_private_key(self) -> str:
        return open(self.jwt_private_key_path, "r").read()

    @property
    def jwt_public_key(self) -> str:
        return open(self.jwt_public_key_path, "r").read()

    redis_host: str
    redis_port: int

    rate_limit_window_sec: int
    rate_limit_max_requests: int

    yandex_client_id: Optional[str] = None
    yandex_client_secret: Optional[str] = None
    yandex_redirect_uri: Optional[str] = None

    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: Optional[str] = None

    # OpenTelemetry / Jaeger
    otel_sampling_ratio: float = 1.0
    otel_service_name: str = "auth-service"
    otel_service_version: str = "0.1.0"
    otel_environment: str = "local"
    otel_exporter_otlp_endpoint: Optional[str] = None

    testing: bool = False  # 👈 по умолчанию False
    enable_tracer: bool = False

    rate_limit_window_sec: int = 60
    rate_limit_max_requests: int = 100

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @model_validator(mode="after")
    def validate_optional_features(self):
        if self.enable_tracer and not self.otel_exporter_otlp_endpoint:
            raise ValueError("otel_exporter_otlp_endpoint is required when ENABLE_TRACER=true")
        return self

    class Config:
        env_file = "auth_service/.env.auth"      # 👈 подхват переменных из .env
        env_prefix = ""
        case_sensitive = False


settings = Settings()