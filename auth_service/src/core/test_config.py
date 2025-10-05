from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    redis_host: str
    redis_port: int

    jwt_algorithm: str
    jwt_private_key_path: str
    jwt_public_key_path: str

    yandex_client_id: str
    yandex_client_secret: str
    yandex_redirect_uri: str

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    otel_sampling_ratio: float
    otel_service_name: str
    otel_service_version: str
    otel_environment: str
    otel_exporter_otlp_endpoint: str

    rate_limit_window_sec: int = 0
    rate_limit_max_requests: int = 9999

    testing: bool = True
    enable_tracer: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        case_sensitive = False
        env_file = ".env.test.auth"  # 👈 будет читать переменные прямо из файла


test_settings = TestSettings()
