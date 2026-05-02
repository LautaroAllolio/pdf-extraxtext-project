import re
import pymupdf
import unicodedata
from typing import Protocol, runtime_checkable
from app.core.exceptions import ApplicationException
from app.core.config import get_settings
from app.services.hashing_service import HashingService

settings = get_settings()


@runtime_checkable
class TextExtractor(Protocol):
    def extract(self, pdf_bytes: bytes) -> tuple[str, int]: ...


class PyMuPdfExtractor:
    def extract(self, pdf_bytes: bytes) -> tuple[str, int]:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        page_count = len(doc)
        doc.close()
        return text.strip(), page_count


class TesseractOcrExtractor:
    mini_dpi = settings.MIN_DPI

    def extract(self, pdf_bytes: bytes) -> tuple[str, int]:
        import pytesseract
        from pdf2image import convert_from_bytes

        images = convert_from_bytes(pdf_bytes, dpi=self.mini_dpi)
        text = "\n".join(
            pytesseract.image_to_string(img, lang="spa+eng")
            for img in images
        )
        return text.strip(), len(images)


class PdfExtractionService:
    def __init__(
        self,
        primary_extractor: TextExtractor,
        fallback_extractor: TextExtractor,
        hashing_service: HashingService | None = None,
    ):
        self._primary  = primary_extractor
        self._fallback = fallback_extractor
        self._hashing  = hashing_service or HashingService()

    def extract_text(self, pdf_bytes: bytes, filename: str) -> dict:
        pdf_hash = self._hashing.calculate_pdf_hash(pdf_bytes)

        text, page_count, method = self._try_primary(pdf_bytes)
        if not text:
            text, page_count, method = self._try_fallback(pdf_bytes)

        text_hash = self._hashing.calculate_text_hash(text) if text else ""

        return {
            "filename": filename,
            "extracted_text": self._normalize_text(text),
            "extraction_method": method,
            "page_count": page_count,
            "pdf_hash": pdf_hash,
            "text_hash": text_hash,
        }

    def _normalize_text(self, text: str) -> str:
        normalized = unicodedata.normalize("NFC", text)
        return re.sub(r'\n{3,}', '\n\n', normalized)

    def _try_primary(self, pdf_bytes: bytes) -> tuple[str, int, str]:
        try:
            text, pages = self._primary.extract(pdf_bytes)
            if len(text) >= settings.MIN_TEXT_LENGTH:
                return text, pages, "pymupdf"
            return "", pages, "pymupdf"
        except Exception:
            return "", 0, "pymupdf"

    def _try_fallback(self, pdf_bytes: bytes) -> tuple[str, int, str]:
        try:
            text, pages = self._fallback.extract(pdf_bytes)
            return text, pages, "ocr"
        except Exception as e:
            raise ApplicationException(f"No se pudo extraer texto del PDF: {str(e)}")