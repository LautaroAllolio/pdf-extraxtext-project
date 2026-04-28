"""
Tests TDD para HashingService - Tests Unitarios.

Este archivo contiene los tests unitarios del servicio de hashing.
NO requiere conexión a base de datos - solo pruebas puras de lógica.

Patrón: TDD Vertical Slices (1 test → código mínimo → siguiente test)

Slices implementados:
    1. Hash de PDF válido → 64 chars hex
    2. ValueError si pdf_bytes=None
    3. ValueError si pdf_bytes vacío
    4. Hash de texto normalizado (lowercase)
    5. Colapsar espacios en texto
    6. Consistencia: mismo texto = mismo hash
    7. ValueError si text=None
    8. ValueError si text vacío
"""

import pytest
from app.services.hashing_service import HashingService


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def hashing_service():
    """
    Fixture que provee una instancia fresca de HashingService.

    Cada test recibe su propia instancia para evitar side effects.
    """
    return HashingService()


# =============================================================================
# SLICE 1: Hash de PDF válido
# =============================================================================

class TestPdfHashHappyPath:
    """Tests del caso feliz para hashing de PDFs."""

    def test_calculate_pdf_hash_returns_64_hex_characters(self, hashing_service):
        """
        Test #1: Un PDF válido debe generar un hash SHA-256 de 64 caracteres hex.

        SHA-256 siempre produce 256 bits = 32 bytes = 64 caracteres hexadecimales.
        Este es el caso "happy path" básico.
        """
        # Arrange: Preparamos datos de prueba
        pdf_bytes = b"%PDF-1.4 fake pdf content for testing"

        # Act: Ejecutamos el método bajo prueba
        result = hashing_service.calculate_pdf_hash(pdf_bytes)

        # Assert: Verificamos el resultado
        assert isinstance(result, str), "El hash debe ser un string"
        assert len(result) == 64, "SHA-256 debe producir exactamente 64 caracteres hex"
        # Verificamos que sea hexadecimal válido (solo contiene 0-9 y a-f)
        assert int(result, 16), "El hash debe ser un número hexadecimal válido"

    def test_calculate_pdf_hash_is_consistent(self, hashing_service):
        """
        Test #1b: El mismo contenido debe producir el mismo hash (determinismo).

        Esta propiedad es fundamental para detectar duplicados.
        """
        pdf_bytes = b"contenido constante"

        hash1 = hashing_service.calculate_pdf_hash(pdf_bytes)
        hash2 = hashing_service.calculate_pdf_hash(pdf_bytes)
        hash3 = hashing_service.calculate_pdf_hash(pdf_bytes)

        assert hash1 == hash2 == hash3, "El hash debe ser determinístico"

    def test_different_content_produces_different_hash(self, hashing_service):
        """
        Test #1c: Contenido diferente debe producir hash diferente.

        Propiedad fundamental de una función hash criptográfica.
        """
        pdf1 = b"contenido A"
        pdf2 = b"contenido B"

        hash1 = hashing_service.calculate_pdf_hash(pdf1)
        hash2 = hashing_service.calculate_pdf_hash(pdf2)

        assert hash1 != hash2, "Hashes de contenido diferente deben ser diferentes"


# =============================================================================
# SLICE 2-3: Validaciones de PDF
# =============================================================================

class TestPdfHashValidations:
    """Tests de validación de entradas para PDF hash."""

    def test_calculate_pdf_hash_raises_value_error_for_none(self, hashing_service):
        """
        Test #2: Debe lanzar ValueError si pdf_bytes es None.

        None no es un valor válido para hashear.
        """
        with pytest.raises(ValueError) as exc_info:
            hashing_service.calculate_pdf_hash(None)  # type: ignore

        assert "None" in str(exc_info.value), "El mensaje debe mencionar None"

    def test_calculate_pdf_hash_raises_value_error_for_empty_bytes(self, hashing_service):
        """
        Test #3: Debe lanzar ValueError si pdf_bytes está vacío.

        Un PDF vacío no tiene sentido hashear.
        """
        with pytest.raises(ValueError) as exc_info:
            hashing_service.calculate_pdf_hash(b"")

        assert "vacío" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()


# =============================================================================
# SLICE 4-5: Normalización de texto
# =============================================================================

class TestTextHashNormalization:
    """Tests de normalización de texto para hashing."""

    def test_calculate_text_hash_returns_64_hex_characters(self, hashing_service):
        """
        Test #4a: Texto válido debe generar hash de 64 caracteres hex.
        """
        text = "Texto de prueba"

        result = hashing_service.calculate_text_hash(text)

        assert isinstance(result, str)
        assert len(result) == 64
        assert int(result, 16)  # Hex válido

    def test_text_hash_ignores_case(self, hashing_service):
        """
        Test #4b: Diferentes capitalizaciones producen el mismo hash.

        "Hola Mundo" y "hola mundo" deben tener el mismo hash.
        """
        hash1 = hashing_service.calculate_text_hash("HOLA MUNDO")
        hash2 = hashing_service.calculate_text_hash("hola mundo")
        hash3 = hashing_service.calculate_text_hash("Hola Mundo")
        hash4 = hashing_service.calculate_text_hash("HoLa MuNdO")

        assert hash1 == hash2 == hash3 == hash4, "Case insensitive hashing failed"

    def test_text_hash_collapses_multiple_spaces(self, hashing_service):
        """
        Test #5a: Múltiples espacios se colapsan en uno solo.

        "hola    mundo" y "hola mundo" deben tener el mismo hash.
        """
        hash1 = hashing_service.calculate_text_hash("hola    mundo")
        hash2 = hashing_service.calculate_text_hash("hola mundo")

        assert hash1 == hash2, "Multiple spaces should be collapsed"

    def test_text_hash_collapses_tabs_and_newlines(self, hashing_service):
        """
        Test #5b: Tabs y newlines también se colapsan como espacios.

        Cualquier whitespace (\s+) se convierte en un espacio simple.
        """
        hash1 = hashing_service.calculate_text_hash("hola\tmundo")
        hash2 = hashing_service.calculate_text_hash("hola mundo")

        hash3 = hashing_service.calculate_text_hash("hola\n\nmundo")
        hash4 = hashing_service.calculate_text_hash("hola mundo")

        assert hash1 == hash2, "Tabs should be treated as spaces"
        assert hash3 == hash4, "Newlines should be treated as spaces"

    def test_text_hash_trims_leading_trailing_spaces(self, hashing_service):
        """
        Test #5c: Espacios al inicio y final se eliminan.

        "  hola mundo  " y "hola mundo" deben tener el mismo hash.
        """
        hash1 = hashing_service.calculate_text_hash("  hola mundo  ")
        hash2 = hashing_service.calculate_text_hash("hola mundo")

        assert hash1 == hash2, "Leading/trailing spaces should be trimmed"

    def test_text_hash_complex_normalization(self, hashing_service):
        """
        Test #5d: Combinación compleja de normalizaciones.

        Este test verifica que todas las normalizaciones funcionen juntas.
        """
        text1 = "  HOLA    MUNDO\n\n\t  este    es   UN   ejemplo  "
        text2 = "hola mundo este es un ejemplo"

        hash1 = hashing_service.calculate_text_hash(text1)
        hash2 = hashing_service.calculate_text_hash(text2)

        assert hash1 == hash2, "Complex normalization should work"


# =============================================================================
# SLICE 6: Consistencia del hash de texto
# =============================================================================

class TestTextHashConsistency:
    """Tests de determinismo del hash de texto."""

    def test_text_hash_is_deterministic(self, hashing_service):
        """
        Test #6: El mismo texto siempre produce el mismo hash.
        """
        text = "texto constante"

        hash1 = hashing_service.calculate_text_hash(text)
        hash2 = hashing_service.calculate_text_hash(text)
        hash3 = hashing_service.calculate_text_hash(text)

        assert hash1 == hash2 == hash3

    def test_different_text_produces_different_hash(self, hashing_service):
        """
        Test #6b: Texto diferente produce hash diferente.
        """
        hash1 = hashing_service.calculate_text_hash("texto uno")
        hash2 = hashing_service.calculate_text_hash("texto dos")

        assert hash1 != hash2


# =============================================================================
# SLICE 7-8: Validaciones de texto
# =============================================================================

class TestTextHashValidations:
    """Tests de validación de entradas para text hash."""

    def test_calculate_text_hash_raises_value_error_for_none(self, hashing_service):
        """
        Test #7: Debe lanzar ValueError si text es None.
        """
        with pytest.raises(ValueError) as exc_info:
            hashing_service.calculate_text_hash(None)  # type: ignore

        assert "None" in str(exc_info.value)

    def test_calculate_text_hash_raises_value_error_for_empty_string(self, hashing_service):
        """
        Test #8: Debe lanzar ValueError si text es string vacío.
        """
        with pytest.raises(ValueError) as exc_info:
            hashing_service.calculate_text_hash("")

        assert "vacío" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()

    def test_calculate_text_hash_raises_for_whitespace_only(self, hashing_service):
        """
        Test #8b: String solo con espacios debe lanzar error (queda vacío tras normalizar).
        """
        with pytest.raises(ValueError) as exc_info:
            hashing_service.calculate_text_hash("     \n\t   ")

        assert "vacío" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()


# =============================================================================
# TESTS COMPARATIVOS (PDF vs Texto)
# =============================================================================

class TestPdfVsTextHash:
    """Tests que comparan los dos métodos de hashing."""

    def test_pdf_and_text_hash_can_be_equal_for_same_content(self, hashing_service):
        """
        El hash de un PDF y su texto pueden ser iguales para el mismo contenido.

        Cuando el contenido binario del PDF es idéntico a la representación
        UTF-8 del texto normalizado, ambos producen el mismo hash SHA-256.
        Esto demuestra la propiedad de determinismo del algoritmo.
        """
        pdf_content = b"contenido"
        text_content = "contenido"

        pdf_hash = hashing_service.calculate_pdf_hash(pdf_content)
        text_hash = hashing_service.calculate_text_hash(text_content)

        # Para el mismo contenido, los hashes pueden ser iguales
        # (el texto se normaliza a minúsculas y se codifica como UTF-8,
        # produciendo los mismos bytes que el PDF original)
        assert pdf_hash == text_hash
