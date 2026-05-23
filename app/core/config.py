from functools import lru_cache
from typing import Optional
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

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    LOG_LEVEL: str = "INFO"

    ROOT_USERNAME: Optional[str] = None
    ROOT_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()