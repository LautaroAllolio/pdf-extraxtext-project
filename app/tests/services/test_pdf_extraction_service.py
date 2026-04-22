import pytest
from unittest.mock import MagicMock
from app.services.pdf_extraction_service import PdfExtractionService
from app.core.exceptions import ValidationException, ApplicationException

VALID_PDF_BYTES = b"%PDF fake content"
INVALID_PDF_BYTES = b"not a pdf"
EMPTY_PDF_BYTES = b"%PDF empty"

def make_service(primary_result = None, fallback_result=None, primary_raises = False, fallback_raises = False):
    """
    simula los testeos  sin necesitar de los archivos pdf
    """
    primary = MagicMock()
    fallback = MagicMock()

    if primary_raises:
        primary.extract.side_effect = Exception("PyMuPDF falló")
    else:
        primary.extract.return_value = primary_result or ("",0)

    if fallback_raises:
        fallback.extract.side_effect = Exception("OCR falló")
    else:
        fallback.extract.return_value = fallback_result or ("",0)

    return PdfExtractionService(primary,fallback), primary, fallback

#Validation ------------------------------------------------------------------------------------------------
def test_archivo_invalido():
    """lanza ValidationException"""
    service, _, _ = make_service()
    with pytest.raises(ValidationException):
        service.extract_text (INVALID_PDF_BYTES, "test.pdf")

#Extractor primario(PyMuPDF)--------------------------------------------------------------------------------
def test_extract_text_pymupdf():
    """Extrae texto usando pymupdf"""
    service, primary, fallback = make_service(
        primary_result =("Texto extraído correctamente", 3)
    )
    result =service. extract_text(VALID_PDF_BYTES, "test_pdf")

    assert result["extraction_method"] == "pymupdf"
    assert result["extracted_text"]    == "Texto extraído correctamente",3
    assert result["page_count"]        == 3
    fallback.extract.assert_not_called()

def test_result_include_filename():
    service, _, _ = make_service(
        primary_result = ("Texto", 1)
    )
    result = service.extract_text(VALID_PDF_BYTES, "mi_archivo.pdf")
    assert result["filename"] == "mi_archivo.pdf"

#Fallback a OCR ---------------------------------------------------------------------------------------------

def test_ocr_if_pymupdf_doesnt_extract():
    #PyMuPDF devuelve vacío por lo que pasa a OCR
    service, primary, fallback = make_service(
        primary_result=("",1 ),
        fallback_result=("Texto OCR", 1)          
    )
    result = service.extract_text(VALID_PDF_BYTES, "escaneado.pdf")

    assert result["extraction_method"] == "ocr"
    assert result["extracted_text"]    == "Texto OCR"
    fallback.extract.assert_called_once()

def test_ocr_if_pymupdf_throw_exception():
    """Si PyMuPDF lanza una excepción pasa a esta función con OCR"""
    service, _, fallback = make_service(
        primary_raises=True,
        fallback_result=("Texto OCR recuperado",2)
    )
    result = service.extract_text(VALID_PDF_BYTES, "roto.pdf")

    assert result["extraction_method"] == "ocr"
    assert result["extracted_text"]    == "Texto OCR recuperado"

# Fallo Total -----------------------------------------------------------------------------------------------

def test_extraction_failed():
    """Lanza una excepcion si PyMuPDF y OCR fallan"""
    service, _, _ = make_service(
    primary_raises=True,
    fallback_raises=True
    )
    with pytest.raises(ApplicationException):
        service.extract_text(VALID_PDF_BYTES, "imposible.pdf")

# Caso Especial ---------------------------------------------------------------------------------------------

def test_text_shorter():
    """
    Si PyMuPDF extrae menos de MIN_TEXT_LENGTH chars,
    se considera vacío y activa el OCR
    """
    service, _, fallback = make_service(
        primary_result=("abc", 1),              #menos de 10 chars
        fallback_result=("Texto completo del OCR",1)
    )
    result = service.extract_text(VALID_PDF_BYTES, "corto.pdf")

    assert result["extraction_method"] == "ocr"
    fallback.extract.assert_called_once()


def text_pdf_vacio():
    service, _, fallback = make_service(
        primary_result=("",0),
        fallback_result=("",0)
    )
    result = service.extract_text(EMPTY_PDF_BYTES, "vacio.pdf")
    fallback.extract.assert_called_once()