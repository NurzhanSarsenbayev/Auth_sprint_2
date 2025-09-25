from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5433
    db_name: str = "auth_test"

    redis_host: str = "localhost"
    redis_port: int = 6380

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_prefix = "TEST_"   # 👈 автоматически подставляет TEST_*
        case_sensitive = False
        env_file = ".env.test"  # 👈 будет читать переменные прямо из файла


test_settings = TestSettings()
