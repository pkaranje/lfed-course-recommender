from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    message: str
    field: str | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    error: ErrorDetail


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: Literal["ok"]
    version: str
    timestamp: datetime
