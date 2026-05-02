"""Tests para el servicio de validación de PDFs.

Siguiendo TDD (Test-Driven Development) y principios de Clean Code:
- Cada test verifica UN comportamiento específico
- Los tests son independientes y repetibles
- Usamos fixtures para setup común
- Nombres descriptivos: test_{escenario}_{resultado_esperado}
"""

import pytest
from io import BytesIO
from unittest.mock import Mock, MagicMock
import pymupdf


@pytest.fixture
def valid_pdf_content():
    """Contenido de un PDF válido mínimo.

    Este es un PDF real de 1 página con el texto "Hello World".
    Se usa para tests que necesitan un PDF válido.
    """
    # PDF mínimo válido con %PDF- header
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000214 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n308\n%%EOF"


@pytest.fixture
def valid_upload_file(valid_pdf_content):
    """Crea un UploadFile mock válido para testing."""
    upload_file = Mock()
    upload_file.filename = "documento.pdf"
    upload_file.content_type = "application/pdf"
    upload_file.read = MagicMock(return_value=valid_pdf_content)
    upload_file.seek = MagicMock()
    return upload_file


class TestPDFExistsValidation:
    """Tests para validación: ¿Existe el archivo?"""

    def test_should_raise_error_when_file_is_none(self):
        """ROJO: Debe lanzar error cuando el archivo es None."""
        # Arrange
        from app.services.pdf_validator import validate_file_exists

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_file_exists(None)

        assert "archivo" in str(exc_info.value).lower() or "file" in str(exc_info.value).lower()

    def test_should_raise_error_when_filename_is_empty(self):
        """ROJO: Debe lanzar error cuando el filename está vacío."""
        # Arrange
        from app.services.pdf_validator import validate_file_exists

        empty_file = Mock()
        empty_file.filename = ""

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_file_exists(empty_file)

        assert "archivo" in str(exc_info.value).lower() or "file" in str(exc_info.value).lower()

    def test_should_pass_when_file_is_valid(self, valid_upload_file):
        """ROJO: Debe pasar cuando el archivo es válido."""
        # Arrange
        from app.services.pdf_validator import validate_file_exists

        # Act - No debe lanzar excepción
        result = validate_file_exists(valid_upload_file)

        # Assert
        assert result is True


class TestPDFSizeValidation:
    """Tests para validación: ¿Pesa más de 0 KB y menos de 50 MB?"""

    def test_should_raise_error_when_file_is_empty(self):
        """ROJO: Debe lanzar error cuando el archivo tiene 0 bytes."""
        # Arrange
        from app.services.pdf_validator import validate_file_size

        empty_content = b""

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_file_size(empty_content)

        assert "vacío" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()

    def test_should_pass_when_file_has_content(self, valid_pdf_content):
        """ROJO: Debe pasar cuando el archivo tiene contenido."""
        # Arrange
        from app.services.pdf_validator import validate_file_size

        # Act & Assert - No debe lanzar excepción
        result = validate_file_size(valid_pdf_content)

        # Assert
        assert result is True

    def test_should_raise_error_when_file_exceeds_50mb(self):
        """ROJO: Debe lanzar error cuando el archivo excede 50 MB."""
        # Arrange
        from app.services.pdf_validator import validate_file_size

        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB en bytes
        oversized_content = b"x" * (MAX_FILE_SIZE + 1)  # 50 MB + 1 byte

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_file_size(oversized_content)

        assert "50 mb" in str(exc_info.value).lower() or "excede" in str(exc_info.value).lower()

    def test_should_pass_when_file_is_at_50mb(self):
        """ROJO: Debe pasar cuando el archivo tiene exactamente 50 MB."""
        # Arrange
        from app.services.pdf_validator import validate_file_size

        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB en bytes
        content_at_limit = b"x" * MAX_FILE_SIZE

        # Act
        result = validate_file_size(content_at_limit)

        # Assert
        assert result is True

    def test_should_pass_when_file_is_under_50mb(self, valid_pdf_content):
        """ROJO: Debe pasar cuando el archivo es menor a 50 MB."""
        # Arrange
        from app.services.pdf_validator import validate_file_size

        # Act
        result = validate_file_size(valid_pdf_content)

        # Assert
        assert result is True


class TestPDFExtensionValidation:
    """Tests para validación: ¿Extensión .pdf?"""

    def test_should_raise_error_when_extension_is_not_pdf(self):
        """ROJO: Debe lanzar error cuando la extensión no es .pdf."""
        # Arrange
        from app.services.pdf_validator import validate_file_extension

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_file_extension("documento.txt")

        assert ".pdf" in str(exc_info.value).lower()

    def test_should_pass_when_extension_is_pdf(self):
        """ROJO: Debe pasar cuando la extensión es .pdf."""
        # Arrange
        from app.services.pdf_validator import validate_file_extension

        # Act
        result = validate_file_extension("documento.pdf")

        # Assert
        assert result is True

    def test_should_pass_when_extension_is_pdf_uppercase(self):
        """ROJO: Debe pasar cuando la extensión es .PDF (mayúsculas)."""
        # Arrange
        from app.services.pdf_validator import validate_file_extension

        # Act
        result = validate_file_extension("documento.PDF")

        # Assert
        assert result is True


class TestPDFHeaderValidation:
    """Tests para validación: ¿Header binario %PDF-?"""

    def test_should_raise_error_when_header_is_invalid(self):
        """ROJO: Debe lanzar error cuando el header no es %PDF-."""
        # Arrange
        from app.services.pdf_validator import validate_pdf_header

        fake_pdf = b"This is not a PDF file"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_pdf_header(fake_pdf)

        assert "pdf" in str(exc_info.value).lower() or "header" in str(exc_info.value).lower()

    def test_should_pass_when_header_is_valid(self, valid_pdf_content):
        """ROJO: Debe pasar cuando el header es %PDF-."""
        # Arrange
        from app.services.pdf_validator import validate_pdf_header

        # Act
        result = validate_pdf_header(valid_pdf_content)

        # Assert
        assert result is True


class TestPDFEncryptionValidation:
    """Tests para validación: ¿Está cifrado?"""

    def test_should_raise_error_when_pdf_is_encrypted(self, monkeypatch):
        """ROJO: Debe lanzar error cuando el PDF está cifrado con contraseña."""
        # Arrange
        from app.services.pdf_validator import validate_not_encrypted

        # Mock de un documento cifrado
        mock_doc = MagicMock()
        mock_doc.needs_pass = True
        mock_doc.close = MagicMock()

        # Patch pymupdf.open para retornar nuestro mock
        def mock_open(*args, **kwargs):
            return mock_doc

        monkeypatch.setattr(pymupdf, "open", mock_open)

        fake_content = b"%PDF-1.4\n<<\n/Encrypt\n>>"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_not_encrypted(fake_content)

        assert "cif" in str(exc_info.value).lower() or "encryp" in str(exc_info.value).lower()

    def test_should_return_document_when_pdf_is_not_encrypted(self, valid_pdf_content, monkeypatch):
        """ROJO: Debe retornar el documento cuando no está cifrado."""
        # Arrange
        from app.services.pdf_validator import validate_not_encrypted

        # Mock de un documento NO cifrado
        mock_doc = MagicMock()
        mock_doc.needs_pass = False
        mock_doc.close = MagicMock()

        def mock_open(*args, **kwargs):
            return mock_doc

        monkeypatch.setattr(pymupdf, "open", mock_open)

        # Act
        result = validate_not_encrypted(valid_pdf_content)

        # Assert
        assert result == mock_doc


class TestPDFPagesValidation:
    """Tests para validación: ¿Tiene páginas?"""

    def test_should_raise_error_when_pdf_has_zero_pages(self):
        """ROJO: Debe lanzar error cuando el PDF tiene 0 páginas."""
        # Arrange
        from app.services.pdf_validator import validate_has_pages

        mock_doc = MagicMock()
        mock_doc.page_count = 0
        mock_doc.close = MagicMock()

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_has_pages(mock_doc)

        assert "página" in str(exc_info.value).lower() or "page" in str(exc_info.value).lower()

    def test_should_pass_when_pdf_has_pages(self):
        """ROJO: Debe pasar cuando el PDF tiene al menos 1 página."""
        # Arrange
        from app.services.pdf_validator import validate_has_pages

        mock_doc = MagicMock()
        mock_doc.page_count = 5

        # Act
        result = validate_has_pages(mock_doc)

        # Assert
        assert result is True


class TestPDFTextValidation:
    """Tests para validación: ¿Tiene texto extraíble?"""

    def test_should_raise_error_when_pdf_has_no_extractable_text(self):
        """ROJO: Debe lanzar error cuando el PDF no tiene texto (ej: escaneado)."""
        # Arrange
        from app.services.pdf_validator import validate_has_text

        mock_page = MagicMock()
        mock_page.get_text.return_value = "   "  # Solo espacios

        mock_doc = MagicMock()
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_doc.close = MagicMock()

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_has_text(mock_doc)

        assert "texto" in str(exc_info.value).lower() or "text" in str(exc_info.value).lower()

    def test_should_pass_when_pdf_has_extractable_text(self):
        """ROJO: Debe pasar cuando el PDF tiene texto extraíble."""
        # Arrange
        from app.services.pdf_validator import validate_has_text

        mock_page = MagicMock()
        mock_page.get_text.return_value = "Este es un texto de prueba con más de 10 caracteres"

        mock_doc = MagicMock()
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))

        # Act
        result = validate_has_text(mock_doc)

        # Assert
        assert result is True


class TestPDFCompleteValidation:
    """Tests de integración: Validación completa del flujo."""

    def test_should_validate_complete_pdf_successfully(
        self, valid_upload_file, valid_pdf_content, monkeypatch
    ):
        """ROJO: Debe validar un PDF completo correctamente paso a paso."""
        # Arrange
        from app.services.pdf_validator import validate_pdf_complete

        # Mock del documento para las validaciones que usan fitz
        mock_doc = MagicMock()
        mock_doc.needs_pass = False
        mock_doc.page_count = 1
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Texto de prueba con suficientes caracteres"
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_doc.close = MagicMock()

        def mock_open(*args, **kwargs):
            return mock_doc

        monkeypatch.setattr(pymupdf, "open", mock_open)

        # Act - Este es el flujo completo
        result = validate_pdf_complete(valid_upload_file, valid_pdf_content)

        # Assert
        assert result is True

    def test_should_stop_at_first_validation_failure(self):
        """ROJO: Debe detenerse en la primera validación que falle."""
        # Arrange
        from app.services.pdf_validator import validate_pdf_complete

        invalid_file = Mock()
        invalid_file.filename = ""  # Archivo inválido

        # Act & Assert
        with pytest.raises(Exception):
            validate_pdf_complete(invalid_file, b"")

    def test_should_pass_for_scanned_pdf_without_text(self, monkeypatch):
        """PDF escaneado sin texto debe pasar validación completa para ir a OCR."""
        from app.services.pdf_validator import validate_pdf_complete

        mock_file = Mock()
        mock_file.filename = "escaneado.pdf"

        mock_doc = MagicMock()
        mock_doc.needs_pass = False
        mock_doc.page_count = 1
        mock_doc.close = MagicMock()

        def mock_open(*args, **kwargs):
            return mock_doc

        monkeypatch.setattr(pymupdf, "open", mock_open)

        content = b"%PDF- escaneado sin texto"

        result = validate_pdf_complete(mock_file, content)
        assert result is True
