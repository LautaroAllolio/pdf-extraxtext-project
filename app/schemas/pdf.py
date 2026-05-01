"""Schemas Pydantic para operaciones con archivos PDF.

DTOs para request/response de extracción y upload de documentos PDF.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class PdfExtractResponse(BaseModel):
    """DTO de salida del servicio de extracción de texto.

    Contiene el resultado de extraer texto de un PDF, sin persistir
    en base de datos. Usado internamente entre servicios.
    """

    filename: str = Field(description="Nombre del archivo original")
    extracted_text: str = Field(description="Texto extraído del PDF")
    extraction_method: str = Field(
        description="Método usado: 'pymupdf' o 'ocr'"
    )
    page_count: int = Field(description="Cantidad de páginas procesadas")


class PdfUploadResponse(BaseModel):
    """DTO de respuesta del endpoint POST /api/v1/pdf/upload.

    Representa un documento PDF persistido en MongoDB con su ID
    asignado por la base de datos.
    """

    id: str = Field(description="ID único generado por MongoDB")
    filename: str = Field(description="Nombre del archivo subido")
    extracted_text: str = Field(description="Texto extraído del PDF")
    extraction_method: str = Field(
        description="Método de extracción: 'pymupdf' o 'ocr'"
    )
    page_count: int = Field(description="Cantidad de páginas del documento")
    pdf_hash: str = Field(description="Hash SHA-256 del contenido binario del PDF")
    text_hash: str = Field(description="Hash SHA-256 del texto normalizado")
    uploaded_at: datetime = Field(description="Timestamp de subida en UTC")


class PdfExtractorError(BaseModel):
    """DTO de error en el proceso de extracción.

    Estructura estandarizada para errores de validación o extracción.
    """

    filename: str = Field(description="Nombre del archivo que causó el error")
    error: str = Field(description="Descripción del error ocurrido")
