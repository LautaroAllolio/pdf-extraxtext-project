import pytest
from fastapi import status

PDF_EXTRACT_URL = "/api/v1/pdfs/extract"

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


@pytest.mark.asyncio
async def test_extract_pdf_exitoso(async_client):
    """PDF válido con texto retorna 200 con los campos correctos."""
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
    assert data["extraction_method"] in ("pymupdf", "ocr")