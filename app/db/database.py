from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings
from app.models.pdf_document import PdfDocument

settings = get_settings()

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def init_database() -> None:
    global _client, _database

    _client = AsyncIOMotorClient(settings.MONGODB_URL)
    _database = _client[settings.MONGODB_DATABASE]
    await init_beanie(database=_database, document_models=[PdfDocument])


async def close_database() -> None:
    global _client, _database
    if _client:
        _client.close()
        _client = None
    _database = None


async def get_database() -> AsyncIOMotorDatabase:
    if _database is None:
        raise RuntimeError("Base de datos no inicializada.")
    return _database
