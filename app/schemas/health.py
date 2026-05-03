from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Schema de respuesta del endpoint de healthcheck."""

    status: str
    version: str