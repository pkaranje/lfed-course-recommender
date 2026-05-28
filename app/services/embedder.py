from app.domain.query import validate_user_query
from app.repositories.embed_client import EmbedClient, EmbedClientError
from app.services import BaseService, ServiceError


class EmbeddingError(ServiceError):
    pass


class EmbedderService(BaseService):
    def __init__(self, embed_client: EmbedClient) -> None:
        self._client = embed_client

    def embed(self, text: str) -> list[float]:
        """Embed text into a vector after validating the input.

        Args:
            text: Input text to embed.

        Returns:
            Embedding vector as list of floats.

        Raises:
            EmbeddingError: On embedding failure.
            QueryEmptyError: If text is empty after sanitisation.
            QueryTooLongError: If text exceeds max length.
        """
        clean = validate_user_query(text)
        try:
            embedding = self._client.embed(clean)
        except EmbedClientError as exc:
            raise EmbeddingError(f"Failed to embed text: {exc}") from exc
        self.logger.info("embedding_created", dimensions=len(embedding))
        return embedding
