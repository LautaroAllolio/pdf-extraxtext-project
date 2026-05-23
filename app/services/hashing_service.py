import hashlib
import re


class HashingService:
    def __init__(self) -> None:
        self._whitespace_pattern = re.compile(r"\s+")

    def calculate_pdf_hash(self, pdf_bytes: bytes) -> str:
        if pdf_bytes is None:
            raise ValueError("pdf_bytes no puede ser None")
        if len(pdf_bytes) == 0:
            raise ValueError("pdf_bytes no puede estar vacío")

        hasher = hashlib.sha256()
        hasher.update(pdf_bytes)
        return hasher.hexdigest()

    def calculate_text_hash(self, text: str) -> str:
        if text is None:
            raise ValueError("text no puede ser None")
        if len(text) == 0:
            raise ValueError("text no puede estar vacío")

        normalized = self._whitespace_pattern.sub(" ", text.lower()).strip()

        if len(normalized) == 0:
            raise ValueError("text no puede estar vacío después de normalizar")

        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()