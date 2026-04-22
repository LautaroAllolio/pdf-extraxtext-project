from pydantic import BaseModel

class PdfExtractResponse(BaseModel):
    """Es la respuesta que se le da al usuario"""
    filename: str
    extracted_text: str
    extraction_method: str
    page_count: int

class PdfExtractorError(BaseModel):
    """Respuesta de error en extracción"""
    filename: str
    error: str