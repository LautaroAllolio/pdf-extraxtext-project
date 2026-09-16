import pytest
from io import BytesIO
from unittest.mock import Mock, MagicMock
import pymupdf


@pytest.fixture
def valid_pdf_content():
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000214 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n308\n%%EOF"


@pytest.fixture
def valid_upload_file(valid_pdf_content):
    upload_file = Mock()
    upload_file.filename = "documento.pdf"
    upload_file.content_type = "application/pdf"
    upload_file.read = MagicMock(return_value=valid_pdf_content)
    upload_file.seek = MagicMock()
    return upload_file


class TestPDFExistsValidation:

    def test_should_raise_error_when_file_is_none(self):
        from app.services.pdf_validator import validate_file_exists

        with pytest.raises(Exception) as exc_info:
            validate_file_exists(None)

        assert "archivo" in str(exc_info.value).lower() or "file" in str(exc_info.value).lower()

    def test_should_raise_error_when_filename_is_empty(self):
        from app.services.pdf_validator import validate_file_exists

        empty_file = Mock()
        empty_file.filename = ""

        with pytest.raises(Exception) as exc_info:
            validate_file_exists(empty_file)

        assert "archivo" in str(exc_info.value).lower() or "file" in str(exc_info.value).lower()

    def test_should_pass_when_file_is_valid(self, valid_upload_file):
        from app.services.pdf_validator import validate_file_exists

        assert validate_file_exists(valid_upload_file) is None


class TestPDFSizeValidation:

    def test_should_raise_error_when_file_is_empty(self):
        from app.services.pdf_validator import validate_file_size

        empty_content = b""

        with pytest.raises(Exception) as exc_info:
            validate_file_size(empty_content)

        assert "vacío" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()

    def test_should_pass_when_file_has_content(self, valid_pdf_content):
        from app.services.pdf_validator import validate_file_size

        assert validate_file_size(valid_pdf_content) is None

    def test_should_raise_error_when_file_exceeds_50mb(self):
        from app.services.pdf_validator import validate_file_size
        from app.core.config import get_settings

        MAX_FILE_SIZE = get_settings().MAX_FILE_SIZE_BYTES * 1024 * 1024
        oversized_content = b"x" * (MAX_FILE_SIZE + 1)  

        with pytest.raises(Exception) as exc_info:
            validate_file_size(oversized_content)

        assert "50 mb" in str(exc_info.value).lower() or "excede" in str(exc_info.value).lower()

    def test_should_pass_when_file_is_at_50mb(self):
        from app.services.pdf_validator import validate_file_size
        from app.core.config import get_settings

        MAX_FILE_SIZE = get_settings().MAX_FILE_SIZE_BYTES * 1024 * 1024
        content_at_limit = b"x" * MAX_FILE_SIZE

        assert validate_file_size(content_at_limit) is None

    def test_should_pass_when_file_is_under_50mb(self, valid_pdf_content):
        from app.services.pdf_validator import validate_file_size

        assert validate_file_size(valid_pdf_content) is None


class TestPDFExtensionValidation:

    def test_should_raise_error_when_extension_is_not_pdf(self):
        from app.services.pdf_validator import validate_file_extension

        with pytest.raises(Exception) as exc_info:
            validate_file_extension("documento.txt")

        assert ".pdf" in str(exc_info.value).lower()

    def test_should_pass_when_extension_is_pdf(self):
        from app.services.pdf_validator import validate_file_extension

        assert validate_file_extension("documento.pdf") is None

    def test_should_pass_when_extension_is_pdf_uppercase(self):
        from app.services.pdf_validator import validate_file_extension

        assert validate_file_extension("documento.PDF") is None


class TestPDFHeaderValidation:

    def test_should_raise_error_when_header_is_invalid(self):
        from app.services.pdf_validator import validate_pdf_header

        fake_pdf = b"This is not a PDF file"

        with pytest.raises(Exception) as exc_info:
            validate_pdf_header(fake_pdf)

        assert "pdf" in str(exc_info.value).lower() or "header" in str(exc_info.value).lower()

    def test_should_pass_when_header_is_valid(self, valid_pdf_content):
        from app.services.pdf_validator import validate_pdf_header

        assert validate_pdf_header(valid_pdf_content) is None


class TestPDFEncryptionValidation:

    def test_should_raise_error_when_pdf_is_encrypted(self, monkeypatch):
        from app.services.pdf_validator import validate_not_encrypted

        mock_doc = MagicMock()
        mock_doc.needs_pass = True
        mock_doc.close = MagicMock()

        def mock_open(*args, **kwargs):
            return mock_doc

        monkeypatch.setattr(pymupdf, "open", mock_open)

        fake_content = b"%PDF-1.4\n<<\n/Encrypt\n>>"

        with pytest.raises(Exception) as exc_info:
            validate_not_encrypted(fake_content)

        assert "cif" in str(exc_info.value).lower() or "encryp" in str(exc_info.value).lower()

    def test_should_return_document_when_pdf_is_not_encrypted(self, valid_pdf_content, monkeypatch):
        from app.services.pdf_validator import validate_not_encrypted

        mock_doc = MagicMock()
        mock_doc.needs_pass = False
        mock_doc.close = MagicMock()

        def mock_open(*args, **kwargs):
            return mock_doc

        monkeypatch.setattr(pymupdf, "open", mock_open)

        result = validate_not_encrypted(valid_pdf_content)

        assert result == mock_doc


class TestPDFPagesValidation:

    def test_should_raise_error_when_pdf_has_zero_pages(self):
        from app.services.pdf_validator import validate_has_pages

        mock_doc = MagicMock()
        mock_doc.page_count = 0
        mock_doc.close = MagicMock()

        with pytest.raises(Exception) as exc_info:
            validate_has_pages(mock_doc)

        assert "página" in str(exc_info.value).lower() or "page" in str(exc_info.value).lower()

    def test_should_pass_when_pdf_has_pages(self):
        from app.services.pdf_validator import validate_has_pages

        mock_doc = MagicMock()
        mock_doc.page_count = 5

        assert validate_has_pages(mock_doc) is None




class TestPDFCompleteValidation:

    def test_should_validate_complete_pdf_successfully(
        self, valid_upload_file, valid_pdf_content, monkeypatch
    ):
        from app.services.pdf_validator import validate_pdf_complete

        mock_doc = MagicMock()
        mock_doc.needs_pass = False
        mock_doc.page_count = 1
        mock_doc.close = MagicMock()

        def mock_open(*args, **kwargs):
            return mock_doc

        monkeypatch.setattr(pymupdf, "open", mock_open)

        result = validate_pdf_complete(valid_upload_file, valid_pdf_content)
        assert result is True

    def test_should_stop_at_first_validation_failure(self):
        from app.services.pdf_validator import validate_pdf_complete

        invalid_file = Mock()
        invalid_file.filename = ""  

        with pytest.raises(Exception):1
            validate_pdf_complete(invalid_file, b"")

    def test_should_pass_for_scanned_pdf_without_text(self, monkeypatch):
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
