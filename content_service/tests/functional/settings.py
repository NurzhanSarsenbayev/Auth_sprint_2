from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):

    PROJECT_NAME: str = "movies"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    ELASTIC_HOST: str = "elasticsearch"
    ELASTIC_PORT: int = 9200
    ELASTIC_INDEX: str = "movies"
    ELASTIC_ID_FIELD: str = "uuid"

    API_HOST: str = "tests_api"
    API_PORT: int = 8000

    # --- Backoff/wait params ---
    WAIT_MAX_ATTEMPTS: int = 40
    WAIT_BASE_DELAY: float = 0.25
    WAIT_MAX_DELAY: float = 3.0

    class Config:
        env_prefix = "TEST_"
        case_sensitive = False


settings = TestSettings()
