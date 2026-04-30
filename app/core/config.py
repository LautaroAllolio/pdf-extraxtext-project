"""
Configuración centralizada de la aplicación.

Utiliza Pydantic Settings para la gestión de configuraciones
con validación de tipos y valores por defecto.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuraciones de la aplicación cargadas desde variables de entorno.
    """

    # Información del proyecto
    PROJECT_NAME: str = "FastAPI Clean Architecture MongoDB"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API con arquitectura de tres capas, Clean Code y MongoDB"

    # Configuración de la API
    API_V1_STR: str = "/api/v1"

    # Configuración de MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017/fastapi_db"
    MONGODB_DATABASE: str = "fastapi_db"

    # Configuración de validación de PDFs
    MAX_FILE_SIZE_BYTES:int = 50
    #Configuración Servicio de extracción PDFs
    MIN_TEXT_LENGTH:int = 10
    MIN_DPI:int = 300

    # Configuración de seguridad
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Configuración de logging
    LOG_LEVEL: str = "INFO"

    # Configuración de root user (opcional)
    ROOT_USERNAME: Optional[str] = None
    ROOT_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = True
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de la configuración.

    El cacheo evita múltiples lecturas del archivo .env
    y mejora el rendimiento.

    Returns:
        Settings: Instancia de configuración de la aplicación.
    """
    return Settings()
