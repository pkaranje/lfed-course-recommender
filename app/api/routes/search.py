from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.schemas.course import CourseCard
from app.core.dependencies import get_retriever_service
from app.domain.query import QueryEmptyError, QueryTooLongError
from app.domain.recommendation import InvalidTopKError
from app.services.retriever import RetrieverError, RetrieverService

router = APIRouter(tags=["search"])


@router.get("/search", response_model=list[CourseCard])
def search(
    q: str = Query(..., min_length=1, max_length=500),
    category: str | None = Query(default=None),
    top_k: int = Query(default=5, ge=1, le=5),
    retriever: RetrieverService = Depends(get_retriever_service),
) -> list[CourseCard]:
    """Direct similarity search against the course vector store."""
    try:
        results = retriever.retrieve(query=q, top_k=top_k, category=category)
        return [
            CourseCard(
                title=c.get("title", ""),
                url=c.get("url", ""),
                category=c.get("category", ""),
                level=c.get("level", ""),
                cert_available=c.get("cert_available", False),
                relevance_score=c.get("score"),
            )
            for c in results
        ]
    except (QueryTooLongError, QueryEmptyError, InvalidTopKError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RetrieverError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
