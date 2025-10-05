from pydantic_settings import BaseSettings


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

    yandex_client_id: str
    yandex_client_secret: str
    yandex_redirect_uri: str

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    # OpenTelemetry / Jaeger
    otel_sampling_ratio: float
    otel_service_name: str
    otel_service_version: str
    otel_environment: str
    otel_exporter_otlp_endpoint: str

    testing: bool = False  # 👈 по умолчанию False
    enable_tracer: bool = True

    rate_limit_window_sec: int = 60
    rate_limit_max_requests: int = 100

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = "auth_service/.env.auth"      # 👈 подхват переменных из .env
        env_prefix = ""
        case_sensitive = False


settings = Settings()