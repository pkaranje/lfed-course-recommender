from app.domain.recommendation import validate_top_k
from app.repositories.vector_store import VectorStoreRepository
from app.services import BaseService, ServiceError
from app.services.embedder import EmbedderService


class RetrieverError(ServiceError):
    pass


class RetrieverService(BaseService):
    def __init__(
        self,
        vector_store: VectorStoreRepository,
        embedder: EmbedderService,
    ) -> None:
        self._store = vector_store
        self._embedder = embedder

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
    ) -> list[dict]:
        """Retrieve top-k courses most relevant to the query.

        Args:
            query: Natural language query string.
            top_k: Number of results to return.
            category: Optional course category filter.

        Returns:
            List of course metadata dicts with similarity scores.

        Raises:
            RetrieverError: If no results are found.
            InvalidTopKError: If top_k is outside the allowed range.
        """
        validate_top_k(top_k)
        embedding = self._embedder.embed(query)
        where = {"category": {"$eq": category}} if category else None
        results = self._store.query(embedding=embedding, n_results=top_k, where=where)
        if not results:
            raise RetrieverError("No courses found for the given query")
        self.logger.info(
            "retrieval_complete",
            count=len(results),
            top_course=results[0].get("title", "unknown"),
        )
        return results
