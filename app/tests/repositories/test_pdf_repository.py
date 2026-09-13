import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestGetByPdfHash:

    @pytest.mark.asyncio
    async def test_returns_none_when_hash_is_empty(self):
        from app.repositories.pdf_repository import PdfRepository
        repo = PdfRepository()
        result = await repo.get_by_pdf_hash("")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_hash_is_not_found(self):
        from app.repositories.pdf_repository import PdfRepository
        repo = PdfRepository()

        with patch(
            "app.repositories.pdf_repository.PdfDocument.find_one",
            new=AsyncMock(return_value=None)
        ):
            result = await repo.get_by_pdf_hash("hash_inexistente")
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_document_when_hash_exists(self):
        from app.repositories.pdf_repository import PdfRepository
        repo = PdfRepository()
        mock_doc = MagicMock()
        mock_doc.pdf_hash = "abc123"

        with patch(
            "app.repositories.pdf_repository.PdfDocument.find_one",
            new=AsyncMock(return_value=mock_doc)
        ):
            result = await repo.get_by_pdf_hash("abc123")
            assert result == mock_doc

class TestGetByTextHash:

    @pytest.mark.asyncio
    async def test_returns_none_when_hash_is_empty(self):
        from app.repositories.pdf_repository import PdfRepository
        repo = PdfRepository()
        result = await repo.get_by_text_hash("")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_hash_is_not_found(self):
        from app.repositories.pdf_repository import PdfRepository
        repo = PdfRepository()

        with patch(
            "app.repositories.pdf_repository.PdfDocument.find_one",
            new=AsyncMock(return_value=None)
        ):
            result = await repo.get_by_text_hash("hash_inexistente")
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_document_when_hash_exists(self):
        from app.repositories.pdf_repository import PdfRepository
        repo = PdfRepository()
        mock_doc = MagicMock()
        mock_doc.text_hash = "abc123"

        with patch(
            "app.repositories.pdf_repository.PdfDocument.find_one",
            new=AsyncMock(return_value=mock_doc)
        ):
            result = await repo.get_by_text_hash("abc123")
            assert result == mock_doc

class TestGetById:

    @pytest.mark.asyncio
    async def test_returns_none_on_invalid_id(self):
        from app.repositories.pdf_repository import PdfRepository
        repo = PdfRepository()
        result = await repo.get_by_id("id-invalido")
        assert result is None

    @pytest.mark.asyncio
    async def test_propagates_infrastructure_errors(self):
        from app.repositories.pdf_repository import PdfRepository
        repo = PdfRepository()

        with patch(
            "app.repositories.pdf_repository.PdfDocument.get",
            new=AsyncMock(side_effect=ConnectionError("base de datos no disponible"))
        ):
            with pytest.raises(ConnectionError):
                await repo.get_by_id("507f1f77bcf86cd799439011")

class TestDeleteById:

    @pytest.mark.asyncio
    async def test_returns_false_on_invalid_id(self):
        from app.repositories.pdf_repository import PdfRepository
        repo = PdfRepository()
        result = await repo.delete_by_id("id-invalido")
        assert result is False

    @pytest.mark.asyncio
    async def test_propagates_infrastructure_errors(self):
        from app.repositories.pdf_repository import PdfRepository
        repo = PdfRepository()

        with patch(
            "app.repositories.pdf_repository.PdfDocument.get",
            new=AsyncMock(side_effect=ConnectionError("base de datos no disponible"))
        ):
            with pytest.raises(ConnectionError):
                await repo.delete_by_id("507f1f77bcf86cd799439011")