"""Repositorio para operaciones CRUD de documentos PDF.

Implementa el patrón Repository para la entidad PdfDocument,
utilizando BaseRepository para operaciones genéricas.
"""

from app.models.pdf_document import PdfDocument
from app.repositories.base import BaseRepository


class PdfRepository(BaseRepository[PdfDocument]):
    """Repositorio para gestionar documentos PDF en MongoDB.

    Hereda de BaseRepository todas las operaciones CRUD genéricas.
    Agrega métodos específicos para consultas por PDF.

    Ejemplo de uso:
    >>> from app.repositories.pdf_repository import PdfRepository
    >>> repo = PdfRepository()
    >>> doc = await repo.create({"filename": "test.pdf", ...})
    >>> found = await repo.get_by_pdf_hash(doc.pdf_hash)
    """

    def __init__(self) -> None:
        """Inicializa el repositorio con el modelo PdfDocument."""
        super().__init__(PdfDocument)

    async def get_by_pdf_hash(self, pdf_hash: str) -> PdfDocument | None:
        if not pdf_hash:
            return None
        return await self._document_model.find_one({"pdf_hash": pdf_hash})

    async def get_by_text_hash(self, text_hash: str) -> PdfDocument | None:
        if not text_hash:
            return None
        return await self._document_model.find_one({"text_hash": text_hash})

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[PdfDocument]:
        """Obtiene todos los documentos ordenados por fecha de subida descendente.

        Args:
            skip: Número de documentos a omitir.
            limit: Número máximo de documentos a retornar.

        Returns:
            Lista de documentos ordenados por uploaded_at desc.
        """
        return await self._document_model.find().sort(
            -self._document_model.uploaded_at
        ).skip(skip).limit(limit).to_list()
