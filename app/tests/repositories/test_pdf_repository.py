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