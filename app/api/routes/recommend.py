from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.schemas.query import RecommendRequest, RecommendResponse
from app.core.dependencies import get_recommend_service
from app.core.limiter import limiter
from app.domain.query import QueryEmptyError, QueryTooLongError
from app.services.llm import LLMError
from app.services.recommend import RecommendService
from app.services.retriever import RetrieverError

router = APIRouter(tags=["recommend"])


@router.post("/recommend", response_model=RecommendResponse)
@limiter.limit("10/minute")
def recommend(
    request: Request,
    body: RecommendRequest,
    service: RecommendService = Depends(get_recommend_service),
) -> RecommendResponse:
    """Run the full RAG pipeline and return a personalised learning roadmap."""
    try:
        return service.recommend(
            skills=body.skills,
            goal=body.goal,
            category=body.category,
        )
    except (QueryTooLongError, QueryEmptyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RetrieverError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
