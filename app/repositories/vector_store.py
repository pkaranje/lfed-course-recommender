from app.repositories import BaseRepository


class VectorStoreRepository(BaseRepository):
    def __init__(self) -> None:
        self._client = None
        self._collection = None

    def _connect(self) -> None:
        raise NotImplementedError

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        """Upsert documents into the ChromaDB collection.

        Args:
            ids: Document IDs (slugified URLs).
            documents: Raw text documents.
            embeddings: Pre-computed embedding vectors.
            metadatas: Course metadata dicts.
        """
        raise NotImplementedError

    def query(self, embedding: list[float], k: int = 5) -> list[dict]:
        """Query collection by embedding similarity.

        Args:
            embedding: Query vector.
            k: Number of results.

        Returns:
            List of result dicts with document, metadata, and distance.
        """
        raise NotImplementedError

    def count(self) -> int:
        """Return number of documents in the collection."""
        raise NotImplementedError
