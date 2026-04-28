"""
Servicio de hashing para detección de duplicados.

Este servicio proporciona funciones para calcular hashes SHA-256
de archivos PDF y su contenido de texto, permitiendo detectar
duplicados incluso si el nombre del archivo es diferente.

Arquitectura:
    - Algoritmo: SHA-256 (estándar de la industria)
    - Normalización: lowercase + colapsar espacios múltiples
    - Determinístico: mismo input = mismo hash siempre
"""

import hashlib
import re


class HashingService:
    """
    Servicio para calcular hashes SHA-256 de PDFs y texto.

    Este servicio es puro (no tiene estado) y puede ser instanciado
    múltiples veces o reutilizado como singleton.

    Attributes:
        _whitespace_pattern: Patrón regex para normalizar espacios.
    """

    def __init__(self) -> None:
        """Inicializa el servicio con patrones de normalización precompilados."""
        # Precompilamos el regex para mejor performance
        # \s+ coincide con cualquier espacio en blanco (espacios, tabs, newlines)
        # y el + significa "uno o más"
        self._whitespace_pattern = re.compile(r"\s+")

    def calculate_pdf_hash(self, pdf_bytes: bytes) -> str:
        """
        Calcula SHA-256 del contenido binario del PDF.

        Este hash identifica de forma única el archivo PDF completo.
        Dos PDFs con el mismo contenido binario tendrán el mismo hash,
        independientemente de su nombre de archivo.

        Args:
            pdf_bytes: Contenido binario del PDF (bytes crudos del archivo).

        Returns:
            Hash SHA-256 de 64 caracteres hexadecimales en minúsculas.

        Raises:
            ValueError: Si pdf_bytes es None o está vacío (len 0).

        Example:
            >>> service = HashingService()
            >>> with open("documento.pdf", "rb") as f:
            ...     hash = service.calculate_pdf_hash(f.read())
            ...     print(hash)  # 'a3f5...2c9b' (64 chars)
        """
        # Validación de entrada: no podemos hashear algo que no existe
        if pdf_bytes is None:
            raise ValueError("pdf_bytes no puede ser None")
        if len(pdf_bytes) == 0:
            raise ValueError("pdf_bytes no puede estar vacío")

        # SHA-256: estándar de la industria, suficientemente seguro
        # hashlib.sha256() crea un objeto hasher
        # .update() alimenta los bytes
        # .hexdigest() devuelve el hash como string hexadecimal
        hasher = hashlib.sha256()
        hasher.update(pdf_bytes)
        return hasher.hexdigest()

    def calculate_text_hash(self, text: str) -> str:
        """
        Calcula SHA-256 del texto normalizado.

        La normalización permite detectar duplicados semánticos:
        - "Hola   Mundo" y "hola mundo" generan el mismo hash
        - Útil cuando dos PDFs tienen el mismo contenido pero
          diferente formato (fuentes, márgenes, etc.)

        Normalización aplicada:
            1. Minúsculas: "Hola" → "hola"
            2. Colapsar espacios: "a    b" → "a b"

        Args:
            text: Texto extraído del PDF.

        Returns:
            Hash SHA-256 de 64 caracteres hexadecimales en minúsculas.

        Raises:
            ValueError: Si text es None o string vacío.

        Example:
            >>> service = HashingService()
            >>> hash1 = service.calculate_text_hash("Hola   Mundo")
            >>> hash2 = service.calculate_text_hash("hola mundo")
            >>> hash1 == hash2  # True - son el mismo contenido semántico
        """
        # Slice 2-3: Validación de entrada
        if text is None:
            raise ValueError("text no puede ser None")
        if len(text) == 0:
            raise ValueError("text no puede estar vacío")

        # Slice 4-5: Normalización del texto
        # Paso 1: Convertir a minúsculas para ignorar diferencias de capitalización
        normalized = text.lower()

        # Paso 2: Colapsar múltiples espacios en uno solo
        # Ejemplo: "hola    mundo\n\n\testo" → "hola mundo esto"
        normalized = self._whitespace_pattern.sub(" ", normalized)

        # Eliminar espacios al inicio y final (strip)
        normalized = normalized.strip()

        # Si después de normalizar queda vacío, es error
        if len(normalized) == 0:
            raise ValueError("text no puede estar vacío después de normalizar")

        # Convertir a bytes y calcular hash
        # UTF-8 es el encoding estándar para texto
        text_bytes = normalized.encode("utf-8")

        hasher = hashlib.sha256()
        hasher.update(text_bytes)
        return hasher.hexdigest()
