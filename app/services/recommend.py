from app.api.schemas.query import RecommendRequest, RecommendResponse
from app.services import BaseService
from app.services.embedder import EmbedderService
from app.services.llm import LLMService
from app.services.retriever import RetrieverService


class RecommendService(BaseService):
    def __init__(
        self,
        embedder: EmbedderService,
        retriever: RetrieverService,
        llm: LLMService,
    ) -> None:
        self._embedder = embedder
        self._retriever = retriever
        self._llm = llm

    def recommend(self, request: RecommendRequest) -> RecommendResponse:
        """Run full RAG pipeline for a recommendation request.

        Args:
            request: Validated recommendation request.

        Returns:
            RecommendResponse with roadmap and course cards.
        """
        raise NotImplementedError
