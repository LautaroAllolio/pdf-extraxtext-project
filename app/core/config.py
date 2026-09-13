from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Clean Architecture MongoDB"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API con arquitectura de tres capas, Clean Code y MongoDB"
    API_V1_STR: str = "/api/v1"

    MONGODB_URL: str = "mongodb://localhost:27017/fastapi_db"
    MONGODB_DATABASE: str = "fastapi_db"

    MAX_FILE_SIZE_BYTES: int = 50
    MIN_TEXT_LENGTH: int = 10
    MIN_DPI: int = 300

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
