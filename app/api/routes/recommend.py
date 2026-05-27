from fastapi import APIRouter, Depends

from app.api.schemas.query import RecommendRequest, RecommendResponse
from app.core.dependencies import get_recommend_service
from app.services.recommend import RecommendService

router = APIRouter(tags=["recommend"])


@router.post("/recommend", response_model=RecommendResponse)
def recommend(
    request: RecommendRequest,
    service: RecommendService = Depends(get_recommend_service),
) -> RecommendResponse:
    """Run the full RAG pipeline and return a personalised learning roadmap."""
    raise NotImplementedError
