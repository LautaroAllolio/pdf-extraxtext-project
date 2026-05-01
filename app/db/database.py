"""
Configuración de la base de datos MongoDB con Motor.

Motor es el driver async oficial de MongoDB para Python.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie

from app.core.config import get_settings
from app.models.pdf_document import PdfDocument

settings = get_settings()

# Cliente MongoDB asíncrono
client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def init_database():
    """
    Inicializa la conexión a MongoDB y Beanie ODM.

    Esta función debe llamarse al iniciar la aplicación.
    """
    global client, database

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.MONGODB_DATABASE]

    # Inicializar Beanie con los modelos/documentos
    await init_beanie(database=database, document_models=[PdfDocument])


async def close_database():
    """
    Cierra la conexión a MongoDB.

    Esta función debe llamarse al cerrar la aplicación.
    """
    global client
    if client:
        client.close()
        client = None


async def get_database() -> AsyncIOMotorDatabase:
    """
    Retorna la instancia de la base de datos.

    Returns:
        AsyncIOMotorDatabase: Instancia de la base de datos MongoDB.

    Raises:
        RuntimeError: Si la base de datos no ha sido inicializada.
    """
    if database is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return database
