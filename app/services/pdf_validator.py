import os
import pymupdf
from typing import Any
from fastapi import UploadFile, HTTPException
from app.core.config import get_settings

settings = get_settings()

def validate_file_exists(file: UploadFile) -> bool:
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Archivo no proporcionado o sin nombre")
    return True


def validate_file_size(content: bytes) -> bool:
    max_bytes = settings.MAX_FILE_SIZE_BYTES * 1024 * 1024
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Archivo vacío")
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400, 
            detail=f"Archivo excede el tamaño máximo permitido de {settings.MAX_FILE_SIZE_BYTES}MB"
        )
    return True


def validate_file_extension(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    if ext != ".pdf":
        raise HTTPException(status_code=400, detail="Archivo no es un .pdf")
    return True


def validate_pdf_header(content: bytes) -> bool:
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Archivo no tiene header PDF válido")
    return True


def validate_not_encrypted(content: bytes) -> pymupdf.Document:
    doc = pymupdf.open(stream=content, filetype="pdf")
    if doc.needs_pass:
        doc.close()
        raise HTTPException(status_code=400, detail="Archivo PDF está cifrado con contraseña")
    return doc


def validate_has_pages(doc: Any) -> bool:
    if doc.page_count < 1:
        raise HTTPException(status_code=400, detail="Archivo PDF no tiene páginas")
    return True



def validate_pdf_complete(file: Any, content: bytes) -> bool:
    validate_file_exists(file)
    validate_file_size(content)
    validate_file_extension(file.filename)
    validate_pdf_header(content)
    doc = validate_not_encrypted(content)
    try:
        validate_has_pages(doc)
    finally:
        doc.close()

    return True
