from datetime import datetime
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING


class PdfDocument(Document):
    """Como se va a representar el PDF en MongoDB"""
    filename: str
    extracted_text: str
    extraction_method: str  # "pymupdf" | "ocr"
    page_count: int
    pdf_hash: str | None = None
    text_hash: str | None = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "pdf_documents"
        indexes = [
            IndexModel([("pdf_hash", ASCENDING)], unique=True, sparse=True),
            IndexModel([("text_hash", ASCENDING)], sparse=True),
        ]

