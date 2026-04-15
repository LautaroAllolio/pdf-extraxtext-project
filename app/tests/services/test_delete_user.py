"""Tests unitarios para delete_user() en UserService.

Estos tests verifican el comportamiento crítico de eliminación de usuarios,
asegurando que nunca se intente eliminar un usuario inexistente y que
el usuario eliminado sea retornado correctamente.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId

from app.core.exceptions import ResourceNotFoundException
from app.models.user import UserDocument
from app.services.user_service import UserService


@pytest.fixture
def repository_mock():
    """Mock del repositorio de usuarios."""
    return MagicMock()


@pytest.fixture
def user_service(repository_mock):
    """Instancia de UserService con repositorio mockeado."""
    service = UserService()
    service._repository = repository_mock
    return service


@pytest.fixture
def existing_user():
    """Usuario existente en el sistema."""
    user = MagicMock(spec=UserDocument)
    user.id = ObjectId()
    user.email = "user@example.com"
    user.username = "testuser"
    user.hashed_password = "hashed_password"
    user.is_active = True
    user.is_superuser = False
    return user


@pytest.fixture
def nonexistent_user_id():
    """ID de usuario que no existe en el sistema."""
    return "507f1f77bcf86cd799439011"


class TestDeleteUser:
    """Tests unitarios para la eliminación de usuarios."""

    @pytest.mark.asyncio
    async def test_returns_deleted_user_when_id_exists(
        self, user_service, repository_mock, existing_user
    ):
        """Caso feliz: retorna el usuario eliminado tal como estaba antes.

        Verifica que:
        - get_by_id(user_id) retorna un UserDocument
        - delete() es llamado con ese UserDocument
        - El servicio retorna el usuario tal como estaba antes de eliminarlo
        """
        user_id = str(existing_user.id)
        repository_mock.get_by_id = AsyncMock(return_value=existing_user)
        repository_mock.delete = AsyncMock()

        result = await user_service.delete_user(user_id)

        repository_mock.get_by_id.assert_called_once_with(user_id)
        repository_mock.delete.assert_called_once_with(existing_user)
        assert result is existing_user
        assert result.email == "user@example.com"
        assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_raises_exception_when_user_not_found(
        self, user_service, repository_mock, nonexistent_user_id
    ):
        """Usuario inexistente: lanza ResourceNotFoundException.

        Verifica que:
        - get_by_id(user_id) retorna None
        - Se lanza ResourceNotFoundException
        - El mensaje contiene el ID buscado
        - delete() no es llamado en ningún caso
        """
        repository_mock.get_by_id = AsyncMock(return_value=None)
        repository_mock.delete = AsyncMock()

        with pytest.raises(ResourceNotFoundException) as exception_info:
            await user_service.delete_user(nonexistent_user_id)

        assert nonexistent_user_id in str(exception_info.value)
        assert "Usuario" in str(exception_info.value)
        assert exception_info.value.status_code == 404
        repository_mock.get_by_id.assert_called_once_with(nonexistent_user_id)
        repository_mock.delete.assert_not_called()

    