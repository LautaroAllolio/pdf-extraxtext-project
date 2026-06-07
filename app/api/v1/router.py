from fastapi import APIRouter
from app.api.v1.endpoints import pdf_extraction, pdf_documents

api_router = APIRouter()

api_router.include_router(pdf_extraction.router, tags=["Upload and Extract PDF"])
api_router.include_router(pdf_documents.router, tags=["GET PDF Documents"])
