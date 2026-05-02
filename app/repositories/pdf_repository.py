"""Repositorio para operaciones CRUD de documentos PDF.

Implementa el patrón Repository para la entidad PdfDocument,
utilizando BaseRepository para operaciones genéricas.
"""

from datetime import datetime

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
    >>> docs = await repo.get_by_filename("test.pdf")
    """

    def __init__(self) -> None:
        """Inicializa el repositorio con el modelo PdfDocument."""
        super().__init__(PdfDocument)

    async def get_by_filename(self, filename: str) -> list[PdfDocument]:
        """Busca documentos por nombre de archivo exacto.

        Args:
            filename: Nombre del archivo a buscar.

        Returns:
            Lista de documentos con ese nombre.
        """
        return await self._document_model.find(
            self._document_model.filename == filename
        ).to_list()

    async def get_by_extraction_method(
        self, method: str, skip: int = 0, limit: int = 100
    ) -> list[PdfDocument]:
        """Busca documentos por método de extracción.

        Args:
            method: Método de extracción ('pymupdf' o 'ocr').
            skip: Número de documentos a omitir.
            limit: Número máximo de documentos a retornar.

        Returns:
            Lista de documentos con ese método.
        """
        return await self._document_model.find(
            self._document_model.extraction_method == method
        ).skip(skip).limit(limit).to_list()

    async def get_by_date_range(
        self, start: datetime, end: datetime, skip: int = 0, limit: int = 100
    ) -> list[PdfDocument]:
        """Busca documentos por rango de fechas de subida.

        Args:
            start: Fecha inicial (inclusive).
            end: Fecha final (inclusive).
            skip: Número de documentos a omitir.
            limit: Número máximo de documentos a retornar.

        Returns:
            Lista de documentos subidos en ese rango.
        """
        return await self._document_model.find(
            self._document_model.uploaded_at >= start,
            self._document_model.uploaded_at <= end
        ).skip(skip).limit(limit).to_list()

    async def get_latest(self, limit: int = 10) -> list[PdfDocument]:
        """Obtiene los documentos más recientemente subidos.

        Args:
            limit: Número máximo de documentos a retornar.

        Returns:
            Lista de documentos ordenados por fecha descendente.
        """
        return await self._document_model.find().sort(
            -self._document_model.uploaded_at
        ).limit(limit).to_list()

    async def get_by_pdf_hash(self, pdf_hash: str) -> PdfDocument | None:
        if not pdf_hash:
            return None
        return await self._document_model.find_one({"pdf_hash": pdf_hash})

    async def get_by_text_hash(self, text_hash: str) -> PdfDocument | None:
        if not text_hash:
            return None
        return await self._document_model.find_one({"text_hash": text_hash})
        