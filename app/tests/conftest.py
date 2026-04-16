import pytest
import pytest_asyncio

from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture(scope="session")
def test_database():
    # Test database (vacio)
    return {
        "client": None,
        "db": None,
        "info": "placeholder – conectar MongoDB de test cuando esté listo",
    }


@pytest_asyncio.fixture()
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
