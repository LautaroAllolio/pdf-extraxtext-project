from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.core.exceptions import ResourceNotFoundException
from app.models.pdf_document import PdfDocument
from app.repositories.pdf_repository import PdfRepository
from app.schemas.pdf import PdfUploadResponse, build_upload_response

router = APIRouter()


@router.get("/pdfs", response_model=list[PdfUploadResponse])
async def get_all_pdfs() -> list[PdfUploadResponse]:
    documents = await PdfRepository().get_all()
    return [build_upload_response(doc) for doc in documents]


@router.get("/pdfs/{doc_id}", response_model=PdfUploadResponse)
async def get_pdf_by_id(doc_id: str) -> PdfUploadResponse:
    """Obtiene un documento PDF persistido por su ID de MongoDB."""
    document = await PdfRepository().get_by_id(doc_id)

    if not document:
        raise ResourceNotFoundException("PdfDocument", doc_id)

    return build_upload_response(document)


@router.delete("/pdfs/{doc_id}", status_code=204)
async def delete_pdf(doc_id: str):
    deleted = await PdfRepository().delete_by_id(doc_id)
    if not deleted:
        raise ResourceNotFoundException("PdfDocument", doc_id)
    return Response(status_code=204)