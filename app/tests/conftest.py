import pytest
import pytest_asyncio

from httpx import ASGITransport, AsyncClient
from app.main import app
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

@pytest.fixture(scope="session")
def test_database():
    # Test database (vacio)
    return {
        "client": None,
        "db": None,
        "info": "placeholder – conectar MongoDB de test cuando esté listo"
    }

from unittest.mock import AsyncMock, MagicMock

@pytest.fixture()
def user_repository(test_database):
    # Por ahora usamos un mock con los mismos métodos que tiene UserRepository
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=None)
    repo.get_by_username   = AsyncMock(return_value=[])
    repo.email_exists    = AsyncMock(return_value=None)
    repo.username_exists    = AsyncMock(return_value=None)
    return repo

@pytest.fixture()
def user_service(user_repository):
    # return UserService(repository=user_repository)
    service = MagicMock()
    service.repository  = user_repository
    service.get_user    = AsyncMock(return_value=None)
    service.list_users  = AsyncMock(return_value=[])
    service.create_user = AsyncMock(return_value=None)
    service.delete_user = AsyncMock(return_value=True)
    return service


@pytest_asyncio.fixture()
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
