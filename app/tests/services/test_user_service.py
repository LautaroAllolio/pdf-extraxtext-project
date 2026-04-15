"""Tests unitarios para UserService - métodos get_user_by_id y get_user_by_email."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId

from app.core.exceptions import ResourceNotFoundException
from app.models.user import UserDocument
from app.schemas.user import UserUpdate
from app.services.user_service import UserService


@pytest.fixture
def repository_mock():
    """Mock del repositorio de usuarios."""
    return MagicMock()


@pytest.fixture
def user_test(repository_mock):
    """Usuario de prueba con atributos esenciales."""
    user = MagicMock(spec=UserDocument)
    user.id = ObjectId()
    user.email = "test@example.com"
    user.username = "testuser"
    user.hashed_password = "hashed_pwd_2024"
    user.is_active = True
    user.is_superuser = False
    return user


@pytest.fixture
def user_service(repository_mock):
    """Instancia de UserService con repositorio mockeado."""
    service = UserService()
    service._repository = repository_mock
    return service


@pytest.fixture
def nonexistent_user_id():
    """ID de usuario que no existe en el sistema."""
    return "507f1f77bcf86cd799439011"


@pytest.fixture
def nonexistent_email():
    """Email que no existe en el sistema."""
    return "nonexistent@example.com"


class TestGetUserById:
    """Tests para obtener usuario por ID."""

    @pytest.mark.asyncio
    async def test_returns_user_when_id_exists(self, user_service, repository_mock, user_test):
        """Retorna UserDocument cuando el usuario existe."""
        user_id = str(user_test.id)
        repository_mock.get_by_id = AsyncMock(return_value=user_test)

        result = await user_service.get_user_by_id(user_id)

        assert result is user_test
        assert result.email == "test@example.com"
        repository_mock.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_raises_exception_when_id_not_found(
        self, user_service, repository_mock, nonexistent_user_id
    ):
        """Lanza ResourceNotFoundException cuando el usuario no existe."""
        repository_mock.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ResourceNotFoundException) as exception_info:
            await user_service.get_user_by_id(nonexistent_user_id)

        assert nonexistent_user_id in str(exception_info.value)
        assert "Usuario" in str(exception_info.value)
        assert exception_info.value.status_code == 404


class TestGetUserByEmail:
    """Tests para obtener usuario por email."""

    @pytest.mark.asyncio
    async def test_returns_user_when_email_exists(self, user_service, repository_mock, user_test):
        """Retorna UserDocument cuando el email existe."""
        email = user_test.email
        repository_mock.get_by_email = AsyncMock(return_value=user_test)

        result = await user_service.get_user_by_email(email)

        assert result is user_test
        assert result.email == email
        repository_mock.get_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_returns_none_when_email_not_found(
        self, user_service, repository_mock, nonexistent_email
    ):
        """Retorna None cuando el email no existe sin lanzar excepción."""
        repository_mock.get_by_email = AsyncMock(return_value=None)

        result = await user_service.get_user_by_email(nonexistent_email)

        assert result is None
        repository_mock.get_by_email.assert_called_once_with(nonexistent_email)


class TestUpdateUserIntegration:
    """Tests de integración para update_user que utiliza get_user_by_id."""

    @pytest.mark.asyncio
    async def test_verifies_user_exists_before_update(
        self, user_service, repository_mock, user_test
    ):
        """Verifica existencia del usuario antes de actualizar."""
        user_id = str(user_test.id)
        repository_mock.get_by_id = AsyncMock(return_value=user_test)
        repository_mock.email_exists = AsyncMock(return_value=False)
        repository_mock.update = AsyncMock(return_value=user_test)
        update_data = UserUpdate(email="new@example.com")

        await user_service.update_user(user_id, update_data)

        repository_mock.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_returns_updated_user(self, user_service, repository_mock, user_test):
        """Retorna el usuario actualizado después de modificarlo."""
        user_id = str(user_test.id)
        repository_mock.get_by_id = AsyncMock(return_value=user_test)
        repository_mock.email_exists = AsyncMock(return_value=False)
        repository_mock.update = AsyncMock(return_value=user_test)
        update_data = UserUpdate(email="new@example.com")

        result = await user_service.update_user(user_id, update_data)

        assert result is user_test
