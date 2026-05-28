from chromadb import Collection

from app.core.config import Settings, settings as _default_settings
from app.repositories._base import BaseRepository, RepositoryError


class VectorStoreRepository(BaseRepository):
    def __init__(self, settings: Settings = _default_settings) -> None:
        import chromadb

        self._settings = settings
        try:
            self._client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                ssl=False,
                headers={"X-Chroma-Token": ""},
            )
        except Exception as exc:
            raise RepositoryError(f"Failed to create ChromaDB client: {exc}") from exc
        self._collection: Collection | None = None

    def get_or_create_collection(self, name: str) -> Collection:
        self.logger.info("get_or_create_collection_started", name=name)
        try:
            collection = self._client.get_or_create_collection(name=name)
            self.logger.info("get_or_create_collection_complete", name=name)
            return collection
        except Exception as exc:
            raise RepositoryError(
                f"Failed to get/create collection '{name}': {exc}"
            ) from exc

    def _ensure_collection(self) -> Collection:
        if self._collection is None:
            self._collection = self.get_or_create_collection("lf_courses")
        return self._collection

    def upsert(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str],
        embeddings: list[list[float]] | None = None,
    ) -> None:
        """Upsert documents into the ChromaDB collection.

        Args:
            documents: Raw text documents (course descriptions).
            metadatas: Course metadata dicts.
            ids: Document IDs (slugified URLs).
            embeddings: Pre-computed embedding vectors. If None, ChromaDB will
                embed using its default model (must match query dimensions).
        """
        self.logger.info("upsert_started", count=len(ids))
        collection = self._ensure_collection()
        try:
            kwargs: dict = {"documents": documents, "metadatas": metadatas, "ids": ids}
            if embeddings is not None:
                kwargs["embeddings"] = embeddings
            collection.upsert(**kwargs)
            self.logger.info("upsert_complete", count=len(ids))
        except Exception as exc:
            raise RepositoryError(f"Upsert failed: {exc}") from exc

    def query(
        self,
        embedding: list[float],
        n_results: int,
        where: dict | None = None,
    ) -> list[dict]:
        """Query collection by embedding similarity.

        Args:
            embedding: Query vector.
            n_results: Number of results to return.
            where: Optional ChromaDB metadata filter.

        Returns:
            List of dicts with title, description, category, level, url,
            cert_available, distance.
        """
        self.logger.info(
            "query_started", n_results=n_results, filtered=where is not None
        )
        collection = self._ensure_collection()
        try:
            kwargs: dict = {
                "query_embeddings": [embedding],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"],
            }
            if where:
                kwargs["where"] = where
            results = collection.query(**kwargs)
            output = [
                {
                    "title": meta.get("title", ""),
                    "description": doc,
                    "category": meta.get("category", ""),
                    "level": meta.get("level", ""),
                    "url": meta.get("url", ""),
                    "cert_available": meta.get("cert_available", False),
                    "distance": dist,
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ]
            self.logger.info("query_complete", n_results=len(output))
            return output
        except Exception as exc:
            raise RepositoryError(f"Query failed: {exc}") from exc

    def count(self) -> int:
        """Return number of documents in the collection."""
        self.logger.info("count_started")
        collection = self._ensure_collection()
        try:
            n = collection.count()
            self.logger.info("count_complete", count=n)
            return n
        except Exception as exc:
            raise RepositoryError(f"Count failed: {exc}") from exc
