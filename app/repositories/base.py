"""
Repositorio base abstracto que define las operaciones CRUD estándar para MongoDB.

Implementa el patrón Repository para desacoplar la capa de datos
de la lógica de negocio usando Beanie como ODM.
"""

from abc import ABC
from typing import Generic, TypeVar

from beanie import Document
from beanie.operators import In
from bson import ObjectId


DocType = TypeVar("DocType", bound=Document)


class BaseRepository(ABC, Generic[DocType]):
    """
    Repositorio base que proporciona operaciones CRUD genéricas para MongoDB.

    Type Parameters:
        DocType: El tipo del documento Beanie que maneja este repositorio.
    """

    def __init__(self, document_model: type[DocType]):
        """
        Inicializa el repositorio con el modelo de documento correspondiente.

        Args:
            document_model: La clase del documento Beanie.
        """
        self._document_model = document_model

    async def get_by_id(self, doc_id: str) -> DocType | None:
        """
        Obtiene un documento por su ID.

        Args:
            doc_id: Identificador del documento (string de ObjectId).

        Returns:
            La instancia del documento si existe, None en caso contrario.
        """
        try:
            return await self._document_model.get(ObjectId(doc_id))
        except Exception:
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[DocType]:
        """
        Obtiene una lista paginada de documentos.

        Args:
            skip: Número de documentos a omitir (offset).
            limit: Número máximo de documentos a retornar.

        Returns:
            Lista de instancias del documento.
        """
        return await self._document_model.find().skip(skip).limit(limit).to_list()

    async def create(self, data: dict) -> DocType:
        """
        Crea un nuevo documento en la base de datos.

        Args:
            data: Diccionario con los datos a insertar.

        Returns:
            La instancia creada del documento.

        Raises:
            ApplicationException: Si el documento ya existe (índice único duplicado).
        """
        from pymongo.errors import DuplicateKeyError
        from app.core.exceptions import ApplicationException

        try:
            doc = self._document_model(**data)
            await doc.insert()
            return doc
        except DuplicateKeyError as e:
            raise ApplicationException(
                message="El documento ya existe en la base de datos",
                status_code=409,
            ) from e

    async def update(self, doc: DocType, data: dict) -> DocType:
        """
        Actualiza un documento existente.

        Args:
            doc: Instancia del documento a actualizar.
            data: Diccionario con los datos a actualizar.

        Returns:
            La instancia actualizada del documento.
        """
        for field, value in data.items():
            if value is not None and hasattr(doc, field):
                setattr(doc, field, value)

        await doc.save()
        return doc

    async def delete(self, doc: DocType) -> None:
        """
        Elimina un documento de la base de datos.

        Args:
            doc: Instancia del documento a eliminar.
        """
        await doc.delete()

    async def delete_by_id(self, doc_id: str) -> bool:
        """
        Elimina un documento por su ID.

        Args:
            doc_id: Identificador del documento a eliminar.

        Returns:
            True si se eliminó correctamente, False si no existía.
        """
        try:
            doc = await self.get_by_id(doc_id)
            if doc:
                await doc.delete()
                return True
            return False
        except Exception:
            return False
