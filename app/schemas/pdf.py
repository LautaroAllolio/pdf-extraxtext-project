from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PdfExtractResponse(BaseModel):
    """DTO de salida del servicio de extracción de texto."""

    filename: str = Field(description="Nombre del archivo original")
    extracted_text: str = Field(description="Texto extraído del PDF")
    extraction_method: Literal["pymupdf", "ocr"] = Field(
        description="Método usado para extraer el texto"
    )
    page_count: int = Field(description="Cantidad de páginas procesadas")
    pdf_hash: str = Field(
        default="", description="Hash SHA-256 del contenido binario del PDF"
    )
    text_hash: str = Field(
        default="", description="Hash SHA-256 del texto normalizado"
    )


class PdfUploadResponse(BaseModel):
    """DTO de respuesta para documentos PDF persistidos en MongoDB."""

    id: str = Field(description="ID único generado por MongoDB")
    filename: str = Field(description="Nombre del archivo subido")
    extracted_text: str = Field(description="Texto extraído del PDF")
    extraction_method: Literal["pymupdf", "ocr"] = Field(
        description="Método de extracción utilizado"
    )
    page_count: int = Field(description="Cantidad de páginas del documento")
    pdf_hash: str = Field(description="Hash SHA-256 del contenido binario del PDF")
    text_hash: str = Field(description="Hash SHA-256 del texto normalizado")
    uploaded_at: datetime = Field(description="Timestamp de subida en UTC")
