"""
Tests de integración para HashingService - Fase 2: Con BD (PRÓXIMO SPRINT).

Este archivo está preparado para tests que REQUIEREN conexión a MongoDB.
Por ahora está documentado como placeholder - se implementará cuando:
    1. Los modelos PDFDocument tengan campos pdf_hash y text_hash
    2. El repositorio tenga queries por hash
    3. Se configure MongoDB de test

CUANDO ESTÉ LISTO, DESCOMENTAR Y IMPLEMENTAR:
"""

import pytest

# =============================================================================
# PLACEHOLDER - Implementar en próximo sprint
# =============================================================================

# TODO: Importar cuando estén disponibles
# from app.models.pdf_document import PDFDocument
# from app.repositories.pdf_repository import PDFRepository
# from app.db.database import get_database


@pytest.mark.skip(reason="Integración con BD - implementar en siguiente sprint")
class TestHashingServiceWithDatabase:
    """
    Tests de integración que requieren MongoDB.

    Estos tests verifican:
        - Guardado de hashes en documentos PDF
        - Búsqueda de duplicados por pdf_hash
        - Búsqueda de duplicados por text_hash
        - Índices únicos en campos de hash
    """

    def test_save_pdf_with_hashes(self):
        """
        Verifica que se pueda guardar un PDF con sus hashes calculados.

        Steps:
            1. Crear PDFDocument con pdf_hash y text_hash
            2. Guardar en MongoDB
            3. Recuperar y verificar que los hashes se guardaron correctamente
        """
        pass  # Implementar cuando PDFDocument tenga campos de hash

    def test_find_duplicate_by_pdf_hash(self):
        """
        Verifica que se pueda buscar duplicados por pdf_hash.

        Steps:
            1. Insertar un PDF con pdf_hash="abc123..."
            2. Buscar por ese pdf_hash
            3. Debe retornar el documento existente
        """
        pass  # Implementar cuando PDFRepository tenga find_by_pdf_hash()

    def test_find_duplicate_by_text_hash(self):
        """
        Verifica que se pueda buscar duplicados por text_hash.

        Útil cuando el mismo contenido viene de PDFs diferentes (ej: scan vs original).
        """
        pass  # Implementar cuando PDFRepository tenga find_by_text_hash()

    def test_unique_constraint_on_pdf_hash(self):
        """
        Verifica que no se puedan guardar dos PDFs con el mismo pdf_hash.

        El índice único debe lanzar DuplicateKeyError.
        """
        pass  # Implementar cuando haya índice único en pdf_hash

    def test_unique_constraint_on_text_hash(self):
        """
        Verifica que no se puedan guardar dos PDFs con el mismo text_hash.
        """
        pass  # Implementar cuando haya índice único en text_hash


# =============================================================================
# NOTAS PARA IMPLEMENTACIÓN FUTURA
# =============================================================================

"""
CAMBIOS NECESARIOS EN OTROS ARCHIVOS (siguiente sprint):

1. app/models/pdf_document.py:
   - Agregar: pdf_hash: str = ""
   - Agregar: text_hash: str = ""

2. app/db/database.py:
   - Crear índices únicos en pdf_hash y text_hash

3. app/repositories/pdf_repository.py:
   - Agregar: async def find_by_pdf_hash(self, pdf_hash: str) -> PDFDocument | None
   - Agregar: async def find_by_text_hash(self, text_hash: str) -> PDFDocument | None

4. app/services/pdf_extraction_service.py:
   - Inyectar HashingService
   - Calcular y almacenar hashes al extraer texto

5. app/api/v1/endpoints/upload.py (o similar):
   - Usar hashes para detectar duplicados antes de procesar
   - Retornar 409 Conflict si ya existe
"""
