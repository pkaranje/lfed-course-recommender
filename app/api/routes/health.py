from fastapi import APIRouter

from app.api.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return service health status."""
    raise NotImplementedError
