def test_user_repository_carga(user_repository):
    assert user_repository is not None

def test_user_service_carga(user_service):
    assert user_service is not None

def test_database_placeholder(test_database):
    assert isinstance(test_database, dict)

async def test_async_client_carga(async_client):
    assert async_client is not None