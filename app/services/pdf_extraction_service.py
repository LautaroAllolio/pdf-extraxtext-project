from typing import Protocol, runtime_checkable
from app.core.exceptions import ValidationException, ApplicationException
import fitz


@runtime_checkable
class TextExtractor(Protocol):
    """
    Interfaz que devuelve texto+cantidad de páginas
    """

    def extract(self, pdf_bytes:bytes) -> tuple[str, int]:
        """
        Extrae texto de un PDf en bytes.
        Returns: (texto_extraído, cantidad_de_paginas)
        """

class PyMuPdfExtractor:
    """
    Extrae texto digital de PDFs usando PyMuPDF
    """
    def extract(self, pdf_bytes: bytes) -> tuple[str, int]:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        page_count = len(doc)
        doc.close()
        return text.strip(), page_count

class TesseractOcrExtractor:
    """
    Extrae texto de PDFs escaneados usando OCR con Tesseract.
    Se usa cuando PyMuPDF no encuntra texto digital
    """
    MIN_DPI: 300

    def extract(self,pdf_bytes=bytes) -> tuple[str,int]:
        import pytesseract 
        from pdf2image import convert_from_bytes
        
        images = convert_from_bytes(pdf_bytes, dpi=self.MIN_DPI)
        text="\n".join(
            pytesseract.image_to_string(img,lang="spa+eng")
            for img in images
        )
        return text.strip(), len(images)

MIN_TEXT_LENGTH = 10 #mínimo de chars para considerar extracción exitosa

class PdfExtractionService:
    """
    Recibe los dos extractores y valida que sea un PDF real
    primero se intenta con PyMuPDF y sino con OCR
    """

    def __init__(self, primary_extractor:TextExtractor,fallback_extractor: TextExtractor):
        self._primary = primary_extractor
        self._fallback = fallback_extractor

    def extract_text(self, pdf_bytes:bytes, filename: str)->dict:
        """
        Intenta la extracción digital primero, cae en OCR si falla
        Args:
            pdf_bytes: Contenido del PDF en bytes
            filename: Nombre del archivo para el resultado
        Returns:
            Dict con texto, método usado y cantidad de páginas
        Raises: 
            ValidationException: Si el archivo no es un PDF válido
            ApplicationException: Si ambos extractores fallan
        """
        self._validate_pdf(pdf_bytes)

        text, page_count, method = self._try_primary(pdf_bytes)

        if not text:
            text, page_count, method=self._try_fallback(pdf_bytes)
        return {
            "filename": filename,
            "extracted_text": text,
            "extraction_method": method,
            "page_count":page_count, 
        }
    
    def _validate_pdf(self, pdf_bytes:bytes)->None:
        """Valida que los bytes correspondan a un PDF real"""
        if not pdf_bytes.startswith(b"%PDF"):
            raise ValidationException("El archivo no es un PDF válido")
    
    def _try_primary(self, pdf_bytes: bytes) -> tuple[str, int, str]:
        """Intenta extracción con el extractor primario (PyMuPDF)"""
        try:
            text, pages = self._primary.extract(pdf_bytes)
            if len(text) >= MIN_TEXT_LENGTH:
                return text, pages, "pymupdf"
            return "", pages, "pymupdf"
        except Exception:
            return "",0,"pymupdf"

    def _try_fallback(self, pdf_bytes:bytes) -> tuple[str,int, str]:
        """Intetna extracción con OCR como fallback"""
        try:
            text, pages = self._fallback.extract(pdf_bytes)
            return text, pages, "ocr"
        except Exception as e:
            raise ApplicationException(
                f"No se pudo extraer texto del PDF: {str(e)}"
            )