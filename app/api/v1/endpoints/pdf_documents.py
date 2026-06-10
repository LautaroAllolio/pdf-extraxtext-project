from fastapi import APIRouter

from app.core.exceptions import ResourceNotFoundException
from app.repositories.pdf_repository import PdfRepository
from app.schemas.pdf import PdfUploadResponse
from app.models.pdf_document import PdfDocument

router = APIRouter()


def _build_upload_response(document: PdfDocument) -> PdfUploadResponse:
    return PdfUploadResponse(
        id=str(document.id),
        filename=document.filename,
        extracted_text=document.extracted_text,
        extraction_method=document.extraction_method,
        page_count=document.page_count,
        pdf_hash=document.pdf_hash,
        text_hash=document.text_hash,
        uploaded_at=document.uploaded_at,
    )


@router.get("/pdfs", response_model=list[PdfUploadResponse])
async def get_all_pdfs() -> list[PdfUploadResponse]:
    documents = await PdfRepository().get_all()
    return [_build_upload_response(doc) for doc in documents]


@router.get("/pdfs/{doc_id}", response_model=PdfUploadResponse)
async def get_pdf_by_id(doc_id: str) -> PdfUploadResponse:
    """Obtiene un documento PDF persistido por su ID de MongoDB."""
    document = await PdfRepository().get_by_id(doc_id)

    # 404 si el documento no existe en MongoDB
    if not document:
        raise ResourceNotFoundException("PdfDocument", doc_id)

    return _build_upload_response(document)


# TODO: Implementar DELETE /pdfs/{doc_id} para eliminar un documento por su ID.
#       Asignado a: equipo de desarrollo.
#       Notas: Usar PdfRepository().delete_by_id(doc_id) y retornar status 204 No Content.
