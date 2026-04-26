from datetime import datetime
from beanie import Document
from pydantic import Field


class PdfDocument(Document):
    """Como se va a representar el PDF en MongoDB"""
    filename: str
    extracted_text: str
    extraction_method: str  # "pymupdf" | "ocr"
    page_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "pdf_documents"
