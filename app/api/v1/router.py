from fastapi import APIRouter
from app.api.v1.endpoints import pdf

api_router = APIRouter()

api_router.include_router(pdf.router, prefix="/pdfs", tags=["pdfs"])