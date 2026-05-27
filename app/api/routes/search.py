from fastapi import APIRouter, Depends, Query

from app.api.schemas.course import CourseResult
from app.core.dependencies import get_embedder_service, get_retriever_service
from app.services.embedder import EmbedderService
from app.services.retriever import RetrieverService

router = APIRouter(tags=["search"])


@router.get("/search", response_model=list[CourseResult])
def search(
    q: str = Query(..., min_length=1, max_length=500),
    k: int = Query(default=5, ge=1, le=20),
    embedder: EmbedderService = Depends(get_embedder_service),
    retriever: RetrieverService = Depends(get_retriever_service),
) -> list[CourseResult]:
    """Direct similarity search against the course vector store."""
    raise NotImplementedError
