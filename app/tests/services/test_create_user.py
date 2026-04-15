import pytest

from unittest.mock import AsyncMock, MagicMock
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.core.exceptions import (
    DuplicateResourceException,
    ValidationException,
)

def create_mocked_service():
    """    Permite simular el comportamiento de la base de datos sin realizar llamadas reales"""
    service = UserService()
    service._repository = MagicMock()
    service._repository.email_exists    = AsyncMock(return_value=False)
    service._repository.username_exists = AsyncMock(return_value=False)
    service._repository.create          = AsyncMock(return_value=MagicMock(
    email="test@test.com",
    username="testuser",
    hashed_password="$2b$hash...",
    created_at=...,
    updated_at=...
    ))
    return service

async def test_create_user_password_corta():
    """    Test de contraseña inválida(demasiado corta) simulado sin activar la base de datos, es decir mockeado"""
    service = UserService()
    service._repository = MagicMock()
    service._repository.email_exists    = AsyncMock()
    service._repository.username_exists = AsyncMock()
    service._repository.create          = AsyncMock()

    user_data = UserCreate(
        email="test@test.com",
        username="testuser",
        password="123"
    )

    with pytest.raises(ValidationException) as exc_info:
        await service.create_user(user_data)

    assert "6 caracteres" in str(exc_info.value)

    service._repository.email_exists.assert_not_called()
    service._repository.username_exists.assert_not_called()
    service._repository.create.assert_not_called()


async def test_create_user_email_duplicado():
    """test que verifica si el mail ya existe y lanza una excepción"""
    service = UserService()
    service._repository = MagicMock()
    service._repository.email_exists    = AsyncMock(return_value=True)
    service._repository.username_exists = AsyncMock()
    service._repository.create          = AsyncMock()

    user_data = UserCreate(
        email="duplicado@test.com",
        username="testuser",
        password="password123"
    )

    with pytest.raises(DuplicateResourceException) as exc_info:
        await service.create_user(user_data)

    assert "email" in str(exc_info.value).lower()

    service._repository.username_exists.assert_not_called()
    service._repository.create.assert_not_called()


async def test_create_user_username_duplicado():
    """test que crea un usuario ya existente y lanza una excepción"""
    service = UserService()
    service._repository = MagicMock()
    service._repository.email_exists    = AsyncMock(return_value=False)
    service._repository.username_exists = AsyncMock(return_value=True)
    service._repository.create          = AsyncMock()

    user_data = UserCreate(
        email="libre@test.com",
        username="duplicado",
        password="password123"
    )

    with pytest.raises(DuplicateResourceException) as exc_info:
        await service.create_user(user_data)

    assert "username" in str(exc_info.value).lower()

    service._repository.create.assert_not_called()


async def test_create_user_exitoso():
    """valida todo cuando todo sale bien"""
    from unittest.mock import patch

    service = UserService()
    service._repository = MagicMock()
    service._repository.email_exists    = AsyncMock(return_value=False)
    service._repository.username_exists = AsyncMock(return_value=False)

    usuario_mockeado = MagicMock()
    usuario_mockeado.email           = "nuevo@test.com"
    usuario_mockeado.username        = "nuevouser"
    usuario_mockeado.hashed_password = "$2b$algohash"

    service._repository.create = AsyncMock(return_value=usuario_mockeado)

    user_data = UserCreate(
        email="nuevo@test.com",
        username="nuevouser",
        password="password123"
    )

    # Mockeamos _hash_password para evitar llamar bcrypt real
    with patch.object(service, "_hash_password", return_value="$2b$hashmockeado"):
        resultado = await service.create_user(user_data)

    assert resultado.email    == "nuevo@test.com"
    assert resultado.username == "nuevouser"

    call_args = service._repository.create.call_args[0][0]
    assert "password"        not in call_args
    assert "hashed_password" in call_args
    assert call_args["hashed_password"] == "$2b$hashmockeado"
    assert call_args["hashed_password"].startswith("$2b$")

    assert "created_at" in call_args
    assert "updated_at" in call_args