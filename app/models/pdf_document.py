from datetime import datetime, timezone
from typing import Literal

from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING


class PdfDocument(Document):
    """Documento MongoDB que representa un PDF procesado por PaperSoul."""

    filename: str
    extracted_text: str
    extraction_method: Literal["pymupdf", "ocr"]
    page_count: int
    pdf_hash: str | None = None
    text_hash: str | None = None
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "pdf_documents"
        indexes = [
            IndexModel([("pdf_hash", ASCENDING)], unique=True, sparse=True),
            IndexModel([("text_hash", ASCENDING)], sparse=True),
        ]