from fastapi import APIRouter, UploadFile, File
from app.repositories.pdf_repository import PdfRepository
from app.schemas.pdf import PdfExtractResponse
from app.services.pdf_extraction_service import PdfExtractionService, PyMuPdfExtractor, TesseractOcrExtractor
from app.services.pdf_validator import validate_pdf_complete

router = APIRouter()

_service = PdfExtractionService(
    primary_extractor=PyMuPdfExtractor(),
    fallback_extractor=TesseractOcrExtractor(),
)


@router.post("/extract", response_model=PdfExtractResponse)
async def extract_pdf(file: UploadFile = File(...)):
    content = await file.read()
    validate_pdf_complete(file, content)
    result = _service.extract_text(content, file.filename)

    repo = PdfRepository()
    await repo.create(result)

    return result