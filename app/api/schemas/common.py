from pydantic import BaseModel


class ErrorDetail(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
    version: str
    chroma_connected: bool
