from fastapi import APIRouter, UploadFile, File
from app.repositories.pdf_repository import PdfRepository
from app.schemas.pdf import PdfExtractResponse
from app.services.pdf_extraction_service import PdfExtractionService, PyMuPdfExtractor, TesseractOcrExtractor
from app.services.pdf_validator import validate_pdf_complete
from app.services.hashing_service import HashingService

router = APIRouter()

_service = PdfExtractionService(
    primary_extractor=PyMuPdfExtractor(),
    fallback_extractor=TesseractOcrExtractor(),
)


@router.post("/extract", response_model=PdfExtractResponse)
async def extract_pdf(file: UploadFile = File(...)):
    content = await file.read()
    validate_pdf_complete(file, content)

    hashing = HashingService()
    pdf_hash = hashing.calculate_pdf_hash(content)
    repo = PdfRepository()

    existing = await repo.get_by_pdf_hash(pdf_hash)
    if existing:
        return {
            "filename": existing.filename,
            "extracted_text": existing.extracted_text,
            "extraction_method": existing.extraction_method,
            "page_count": existing.page_count,
        }

    result = _service.extract_text(content, file.filename)

    existing_text = await repo.get_by_text_hash(result["text_hash"])
    if existing_text:
        return {
            "filename": existing_text.filename,
            "extracted_text": existing_text.extracted_text,
            "extraction_method": existing_text.extraction_method,
            "page_count": existing_text.page_count,
        }

    await repo.create(result)
    return result