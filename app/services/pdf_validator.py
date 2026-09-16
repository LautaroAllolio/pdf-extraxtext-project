from pathlib import Path
from typing import Any

import pymupdf
from fastapi import HTTPException, UploadFile

from app.core.config import get_settings

settings = get_settings()


def validate_file_exists(file: UploadFile) -> None:
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Archivo no proporcionado o sin nombre")


def validate_file_size(content: bytes) -> None:
    max_bytes = settings.MAX_FILE_SIZE_BYTES * 1024 * 1024
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Archivo vacío")
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo excede el tamaño máximo de {settings.MAX_FILE_SIZE_BYTES} MB",
        )


def validate_file_extension(filename: str) -> None:
    if Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="El archivo debe tener extensión .pdf")


def validate_pdf_header(content: bytes) -> None:
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="El archivo no tiene un header PDF válido")


def validate_not_encrypted(content: bytes) -> pymupdf.Document:
    doc = pymupdf.open(stream=content, filetype="pdf")
    if doc.needs_pass:
        doc.close()
        raise HTTPException(status_code=400, detail="Archivo PDF está cifrado con contraseña")
    return doc


def validate_has_pages(doc: Any) -> None:
    if doc.page_count < 1:
        raise HTTPException(status_code=400, detail="El PDF no tiene páginas")


def validate_has_text(doc: Any) -> bool:
    has_extractable_text = any(
        len(page.get_text().strip()) > settings.MIN_TEXT_LENGTH
        for page in doc
    )
    if not has_extractable_text:
        doc.close()
        raise HTTPException(status_code=400, detail="El PDF no tiene texto extraíble")
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
