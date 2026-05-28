from app.repositories.embed_client import EmbedClient
from app.services import BaseService


class EmbedderService(BaseService):
    def __init__(self, embed_client: EmbedClient) -> None:
        self._client = embed_client

    def embed(self, text: str) -> list[float]:
        """Embed a text string into a vector.

        Args:
            text: Input text to embed.

        Returns:
            Embedding vector as list of floats.
        """
        raise NotImplementedError
