"""Servicio de validación de archivos PDF.

Este módulo implementa las 7 validaciones requeridas:
1. Existe el archivo
2. Pesa más de 0 KB
3. Extensión .pdf
4. Header %PDF-
5. No está cifrado
6. Tiene páginas
7. Tiene texto extraíble
"""
import os
import pymupdf
from typing import Any
from fastapi import UploadFile, HTTPException

def validate_file_exists(file: UploadFile) -> bool:
    """Valida que el archivo exista y tenga nombre."""
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Archivo no proporcionado o sin nombre")
    return True

def validate_file_size(content: bytes) -> bool:
    """Valida que el archivo tenga contenido (> 0 bytes)."""
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Archivo vacío")
    """TODO:Agregar validación de tamaño máximo"""
    return True

def validate_file_extension(filename: str) -> bool:
    """Valida que la extensión sea .pdf (case-insensitive)."""
    ext = os.path.splitext(filename)[1].lower()
    if ext != ".pdf":
        raise HTTPException(status_code=400, detail="Archivo no es un .pdf")
    return True

def validate_pdf_header(content: bytes) -> bool:
    """Valida que el header binario sea %PDF-."""
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Archivo no tiene header PDF válido")
    return True

def validate_not_encrypted(content: bytes) -> pymupdf.Document:
    """Valida que el PDF no esté cifrado con contraseña.

    Retorna el documento fitz abierto si es válido.
    """
    doc = pymupdf.open(stream=content, filetype="pdf")
    if doc.needs_pass:
        doc.close()
        raise HTTPException(status_code=400, detail="Archivo PDF está cifrado con contraseña")
    return doc

def validate_has_pages(doc: Any) -> bool:
    """Valida que el PDF tenga al menos 1 página."""
    if doc.page_count < 1:
        raise HTTPException(status_code=400, detail="Archivo PDF no tiene páginas")
    return True

def validate_has_text(doc: Any) -> bool:
    """Valida que el PDF tenga texto extraíble.

    Umbral: más de 10 caracteres en total.
    """
    has_text = False
    for page in doc:
        text = page.get_text().strip()
        if len(text) > 10:
            has_text = True
            break
    if not has_text:
        doc.close()
        raise HTTPException(status_code=400, detail="Archivo PDF no tiene texto extraíble")
    return True

    
def validate_pdf_complete(file: Any, content: bytes) -> bool:
    """Validación completa: ejecuta todas las validaciones en orden.

    Orden de validaciones:
    1. Existencia
    2. Tamaño
    3. Extensión
    4. Header
    5. Cifrado (retorna doc )
    6. Páginas
    7. Texto
    """
    validate_file_exists(file)
    validate_file_size(content)
    validate_file_extension(file.filename)
    validate_pdf_header(content)
    
    doc = validate_not_encrypted(content)
    try:
        validate_has_pages(doc)
        validate_has_text(doc)
    finally:
        doc.close()
    
    return True