from fastapi import status


async def test_health_returns_200(async_client):
    response = await async_client.get("/health")
    assert response.status_code == status.HTTP_200_OK


async def test_health_payload(async_client):
    response = await async_client.get("/health")
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


async def test_health_response_model(async_client):
    response = await async_client.get("/health")
    data = response.json()
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)