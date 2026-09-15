from fastapi import APIRouter, UploadFile, File

from app.models.pdf_document import PdfDocument
from app.repositories.pdf_repository import PdfRepository
from app.schemas.pdf import PdfExtractResponse, PdfUploadResponse, build_upload_response
from app.services.hashing_service import HashingService
from app.services.pdf_extraction_service import (
    PdfExtractionService,
    PyMuPdfExtractor,
    TesseractOcrExtractor,
)
from app.services.pdf_validator import validate_pdf_complete

router = APIRouter()

_service = PdfExtractionService(
    primary_extractor=PyMuPdfExtractor(),
    fallback_extractor=TesseractOcrExtractor(),
)
_hashing = HashingService()


@router.post("/pdfs/extract", response_model=PdfExtractResponse)
async def extract_pdf(file: UploadFile = File(...)):
    content = await file.read()
    validate_pdf_complete(file, content)

    existing_by_pdf = await _find_duplicate_by_pdf_hash(content)
    if existing_by_pdf:
        return build_upload_response(existing_by_pdf)

    result = _service.extract_text(content, file.filename)

    existing_by_text = await _find_duplicate_by_text_hash(result["text_hash"])
    if existing_by_text:
        return build_upload_response(existing_by_text)

    await _persist_result(result)
    return result


async def _find_duplicate_by_pdf_hash(content: bytes) -> PdfDocument | None:
    pdf_hash = _hashing.calculate_pdf_hash(content)
    return await PdfRepository().get_by_pdf_hash(pdf_hash)


async def _find_duplicate_by_text_hash(text_hash: str) -> PdfDocument | None:
    return await PdfRepository().get_by_text_hash(text_hash)


async def _persist_result(result: dict) -> None:
    await PdfRepository().create(result)