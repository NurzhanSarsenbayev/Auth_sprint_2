from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "auth_db"

    jwt_secret_key: str = "secret"
    jwt_algorithm: str = "HS256"

    redis_host: str = "redis"
    redis_port: int = 6379

    testing: bool = False  # 👈 по умолчанию False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"       # 👈 подхват переменных из .env
        env_prefix = ""
        case_sensitive = False


settings = Settings()
