"""Repositorio para operaciones CRUD de documentos PDF.

Implementa el patrón Repository para la entidad PdfDocument,
utilizando BaseRepository para operaciones genéricas.
"""

from app.models.pdf_document import PdfDocument
from app.repositories.base import BaseRepository


class PdfRepository(BaseRepository[PdfDocument]):
    """Repositorio para gestionar documentos PDF en MongoDB.

    Hereda de BaseRepository todas las operaciones CRUD genéricas.

    Ejemplo de uso:
        >>> from app.repositories.pdf_repository import PdfRepository
        >>> repo = PdfRepository()
        >>> doc = await repo.create({"filename": "test.pdf", ...})
    """

    def __init__(self) -> None:
        """Inicializa el repositorio con el modelo PdfDocument."""
        super().__init__(PdfDocument)
