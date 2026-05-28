import time

from app.api.schemas.course import CourseCard
from app.api.schemas.query import RecommendResponse
from app.core.config import settings
from app.domain.query import validate_user_query
from app.services import BaseService
from app.services.embedder import EmbedderService
from app.services.llm import LLMService
from app.services.retriever import RetrieverService


class RecommendService(BaseService):
    def __init__(
        self,
        embedder: EmbedderService | None = None,
        retriever: RetrieverService | None = None,
        llm: LLMService | None = None,
    ) -> None:
        # Lazy instantiation so the class can be used without explicit DI (e.g. CLI testing).
        # Production code should always inject dependencies via get_recommend_service().
        if embedder is None or retriever is None or llm is None:
            from app.repositories.embed_client import EmbedClient
            from app.repositories.llm_client import LLMClient
            from app.repositories.vector_store import VectorStoreRepository

            _embed_client = EmbedClient()
            _embedder = embedder or EmbedderService(embed_client=_embed_client)
            _retriever = retriever or RetrieverService(
                vector_store=VectorStoreRepository(),
                embedder=_embedder,
            )
            _llm = llm or LLMService(llm_client=LLMClient())
            self._embedder: EmbedderService = _embedder
            self._retriever: RetrieverService = _retriever
            self._llm: LLMService = _llm
        else:
            self._embedder = embedder
            self._retriever = retriever
            self._llm = llm

    def recommend(
        self,
        skills: str,
        goal: str,
        category: str | None = None,
    ) -> RecommendResponse:
        """Run the full RAG pipeline and return a personalised learning roadmap.

        Args:
            skills: Learner's current skills and background.
            goal: Learner's career goal.
            category: Optional course category filter.

        Returns:
            RecommendResponse with roadmap text and list of CourseCards.
        """
        start = time.perf_counter()

        clean_skills = validate_user_query(skills)
        clean_goal = validate_user_query(goal)

        courses = self._retriever.retrieve(
            query=f"{clean_skills} {clean_goal}",
            top_k=settings.TOP_K_RESULTS,
            category=category,
        )

        llm_query = f"Learner background: {clean_skills}\nCareer goal: {clean_goal}"
        roadmap = self._llm.generate(query=llm_query, courses=courses)

        course_cards = [
            CourseCard(
                title=c.get("title", ""),
                url=c.get("url", ""),
                category=c.get("category", ""),
                level=c.get("level"),
                cert_available=c.get("cert_available", False),
            )
            for c in courses
        ]

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self.logger.info(
            "recommend_complete",
            courses_found=len(course_cards),
            duration_ms=duration_ms,
        )

        return RecommendResponse(
            roadmap=roadmap,
            courses=course_cards,
            model_used=settings.LLM_MODEL,
        )
