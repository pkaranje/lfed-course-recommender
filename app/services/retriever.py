from app.repositories.vector_store import VectorStoreRepository
from app.services import BaseService


class RetrieverService(BaseService):
    def __init__(self, vector_store: VectorStoreRepository) -> None:
        self._store = vector_store

    def retrieve(self, embedding: list[float], k: int = 5) -> list[dict]:
        """Retrieve top-k courses by embedding similarity.

        Args:
            embedding: Query embedding vector.
            k: Number of results to return.

        Returns:
            List of course metadata dicts with similarity scores.
        """
        raise NotImplementedError
