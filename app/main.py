"""
Punto de entrada principal de la aplicación FastAPI con MongoDB.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.database import init_database, close_database
from app.schemas.health import HealthResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor del ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.

    Inicializa la conexión a MongoDB y configura Beanie ODM.
    """
    configure_logging()
    await init_database()
    yield
    await close_database()


def create_application() -> FastAPI:
    """
    Factory para crear la instancia de la aplicación FastAPI.

    Returns:
        FastAPI: Instancia configurada de la aplicación.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Verificación de estado del sistema",
)
async def health_check():
    """Retorna el estado operativo de la API y su versión."""
    return HealthResponse(status="healthy", version=settings.VERSION)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
