import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch

PDF_EXTRACT_URL = "/api/v1/pdfs/extract"
PDF_LIST_URL = "/api/v1/pdfs"
PDF_DETAIL_URL = "/api/v1/pdfs/{doc_id}"

VALID_PDF = (
    b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
    b"2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n"
    b"3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n"
    b"/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\n"
    b"BT\n/F1 12 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\n"
    b"xref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n"
    b"0000000115 00000 n\n0000000214 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n"
    b">>\nstartxref\n308\n%%EOF"
)


def _mock_repo():
    mock = AsyncMock()
    mock.get_by_pdf_hash  = AsyncMock(return_value=None)
    mock.get_by_text_hash = AsyncMock(return_value=None)
    mock.create           = AsyncMock(return_value=None)
    return mock


def _mock_repo_with_data(docs: list):
    """Devuelve un mock de PdfRepository con get_all configurado."""
    mock = AsyncMock()
    mock.get_all = AsyncMock(return_value=docs)
    return mock


def _mock_repo_with_get_by_id(doc):
    """Devuelve un mock de PdfRepository con get_by_id configurado."""
    mock = AsyncMock()
    mock.get_by_id = AsyncMock(return_value=doc)
    return mock


@pytest.mark.asyncio
async def test_extract_pdf_exitoso(async_client):
    """PDF válido con texto retorna 200 con los campos correctos."""
    with patch("app.api.v1.endpoints.pdf_extraction.PdfRepository", return_value=_mock_repo()):
        response = await async_client.post(
            PDF_EXTRACT_URL,
            files={"file": ("documento.pdf", VALID_PDF, "application/pdf")},
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "filename" in data
    assert "extracted_text" in data
    assert "extraction_method" in data
    assert "page_count" in data
    assert data["filename"] == "documento.pdf"
    assert data["page_count"] >= 1


@pytest.mark.asyncio
async def test_extract_pdf_archivo_vacio(async_client):
    """Archivo vacío retorna 400."""
    response = await async_client.post(
        PDF_EXTRACT_URL,
        files={"file": ("vacio.pdf", b"", "application/pdf")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_extract_pdf_extension_invalida(async_client):
    """Archivo con extensión distinta a .pdf retorna 400."""
    response = await async_client.post(
        PDF_EXTRACT_URL,
        files={"file": ("documento.txt", VALID_PDF, "text/plain")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_extract_pdf_header_invalido(async_client):
    """Archivo con header inválido (no es PDF real) retorna 400."""
    response = await async_client.post(
        PDF_EXTRACT_URL,
        files={"file": ("falso.pdf", b"esto no es un pdf", "application/pdf")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_extract_pdf_supera_50mb(async_client):
    """Archivo mayor a 50 MB retorna 400."""
    contenido_grande = b"%PDF-" + b"x" * (50 * 1024 * 1024 + 1)
    response = await async_client.post(
        PDF_EXTRACT_URL,
        files={"file": ("grande.pdf", contenido_grande, "application/pdf")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_extract_pdf_response_model(async_client):
    """El response cumple exactamente con el modelo PdfExtractResponse."""
    with patch("app.api.v1.endpoints.pdf_extraction.PdfRepository", return_value=_mock_repo()):
        response = await async_client.post(
            PDF_EXTRACT_URL,
            files={"file": ("documento.pdf", VALID_PDF, "application/pdf")},
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data["filename"], str)
    assert isinstance(data["extracted_text"], str)
    assert isinstance(data["extraction_method"], str)
    assert isinstance(data["page_count"], int)
    assert isinstance(data["pdf_hash"], str)
    assert isinstance(data["text_hash"], str)
    assert data["extraction_method"] in ("pymupdf", "ocr")
    assert len(data["pdf_hash"]) == 64
    assert len(data["text_hash"]) == 64


@pytest.mark.asyncio
async def test_get_all_pdfs_empty(async_client):
    """Cuando no hay documentos, retorna lista vacía []."""
    with patch("app.api.v1.endpoints.pdf_documents.PdfRepository", return_value=_mock_repo_with_data([])):
        response = await async_client.get(PDF_LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_pdfs_with_documents(async_client):
    """Retorna lista de documentos en formato PdfUploadResponse."""
    from datetime import datetime, timezone

    mock_doc_older = AsyncMock()
    mock_doc_older.id = "507f1f77bcf86cd799439011"
    mock_doc_older.filename = "doc1.pdf"
    mock_doc_older.extracted_text = "Texto 1"
    mock_doc_older.extraction_method = "pymupdf"
    mock_doc_older.page_count = 1
    mock_doc_older.pdf_hash = "hash_pdf_1"
    mock_doc_older.text_hash = "hash_text_1"
    mock_doc_older.uploaded_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    mock_doc_newer = AsyncMock()
    mock_doc_newer.id = "507f1f77bcf86cd799439012"
    mock_doc_newer.filename = "doc2.pdf"
    mock_doc_newer.extracted_text = "Texto 2"
    mock_doc_newer.extraction_method = "ocr"
    mock_doc_newer.page_count = 2
    mock_doc_newer.pdf_hash = "hash_pdf_2"
    mock_doc_newer.text_hash = "hash_text_2"
    mock_doc_newer.uploaded_at = datetime(2023, 6, 15, 10, 30, 0, tzinfo=timezone.utc)

    with patch("app.api.v1.endpoints.pdf_documents.PdfRepository", return_value=_mock_repo_with_data([mock_doc_newer, mock_doc_older])):
        response = await async_client.get(PDF_LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

    # Verifica estructura de cada item según PdfUploadResponse
    for doc in data:
        assert "id" in doc
        assert "filename" in doc
        assert "extracted_text" in doc
        assert "extraction_method" in doc
        assert "page_count" in doc
        assert "pdf_hash" in doc
        assert "text_hash" in doc
        assert "uploaded_at" in doc
        assert doc["extraction_method"] in ("pymupdf", "ocr")

    # Orden descendente por uploaded_at: primero el más nuevo
    assert data[0]["filename"] == "doc2.pdf"
    assert data[1]["filename"] == "doc1.pdf"


# =============================================================================
# TESTS TDD PARA GET /api/v1/pdfs/{doc_id}
# =============================================================================

@pytest.mark.asyncio
async def test_get_pdf_by_id_success(async_client):
    """Retorna un PdfDocument existente por su ID de MongoDB."""
    from datetime import datetime, timezone

    mock_doc = AsyncMock()
    mock_doc.id = "507f1f77bcf86cd799439011"
    mock_doc.filename = "informe.pdf"
    mock_doc.extracted_text = "Texto extraído del informe"
    mock_doc.extraction_method = "pymupdf"
    mock_doc.page_count = 5
    mock_doc.pdf_hash = "abc123" * 8  # 64 chars simulados
    mock_doc.text_hash = "def456" * 8
    mock_doc.uploaded_at = datetime(2023, 8, 20, 14, 30, 0, tzinfo=timezone.utc)

    with patch(
        "app.api.v1.endpoints.pdf_documents.PdfRepository",
        return_value=_mock_repo_with_get_by_id(mock_doc),
    ):
        response = await async_client.get(PDF_DETAIL_URL.format(doc_id="507f1f77bcf86cd799439011"))

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Verifica estructura completa según PdfUploadResponse
    assert data["id"] == "507f1f77bcf86cd799439011"
    assert data["filename"] == "informe.pdf"
    assert data["extracted_text"] == "Texto extraído del informe"
    assert data["extraction_method"] == "pymupdf"
    assert data["page_count"] == 5
    assert data["pdf_hash"] == "abc123" * 8
    assert data["text_hash"] == "def456" * 8
    assert "uploaded_at" in data


@pytest.mark.asyncio
async def test_get_pdf_by_id_not_found(async_client):
    """Retorna 404 cuando el doc_id no existe en la base de datos."""
    with patch(
        "app.api.v1.endpoints.pdf_documents.PdfRepository",
        return_value=_mock_repo_with_get_by_id(None),
    ):
        response = await async_client.get(PDF_DETAIL_URL.format(doc_id="id_inexistente"))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "message" in data
    assert "no encontrado" in data["message"].lower()

from unittest.mock import patch
from app.repositories.pdf_repository import PdfRepository

@pytest.mark.asyncio
async def test_delete_pdf_exitoso(async_client):
    doc_id = "507f1f77bcf86cd799439011"
    with patch.object(PdfRepository, "delete_by_id", return_value=True) as mock_delete:
        # URL corregida con "pdfs" 🚨
        response = await async_client.delete(f"/api/v1/pdfs/{doc_id}") 
        assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_pdf_no_existe(async_client):
    doc_id = "507f1f77bcf86cd799439011"
    with patch.object(PdfRepository, "delete_by_id", return_value=False) as mock_delete:
        # URL corregida con "pdfs" 🚨
        response = await async_client.delete(f"/api/v1/pdfs/{doc_id}") 
        assert response.status_code == 404

