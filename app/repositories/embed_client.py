from app.core.config import settings
from app.repositories._base import BaseRepository, RepositoryError


class EmbedClientError(RepositoryError):
    pass


class EmbedClient(BaseRepository):
    def embed(self, text: str) -> list[float]:
        """Embed text using the configured embedding provider.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.

        Raises:
            EmbedClientError: On any SDK failure.
            ValueError: If EMBED_MODEL prefix is not supported.
        """
        model = settings.EMBED_MODEL

        try:
            if model.startswith("ollama/"):
                import ollama

                model_name = model.replace("ollama/", "")
                client = ollama.Client(host=settings.OLLAMA_HOST)
                r = client.embeddings(model=model_name, prompt=text)
                embedding: list[float] = r["embedding"]
                self.logger.info(
                    "embed_complete",
                    provider="ollama",
                    model=model_name,
                    dimensions=len(embedding),
                )
                return embedding

            elif model.startswith("text-embedding"):
                from openai import OpenAI

                r = OpenAI(api_key=settings.OPENAI_API_KEY).embeddings.create(
                    model=model, input=text
                )
                embedding = r.data[0].embedding
                self.logger.info(
                    "embed_complete",
                    provider="openai",
                    model=model,
                    dimensions=len(embedding),
                )
                return embedding

            elif model.startswith("gemini/"):
                import google.generativeai as genai

                model_name = model.replace("gemini/", "")
                genai.configure(api_key=settings.GEMINI_API_KEY)
                r = genai.embed_content(model=model_name, content=text)
                embedding = r["embedding"]
                self.logger.info(
                    "embed_complete",
                    provider="gemini",
                    model=model_name,
                    dimensions=len(embedding),
                )
                return embedding

        except EmbedClientError:
            raise
        except Exception as exc:
            raise EmbedClientError(
                f"Embedding failed for model '{model}': {exc}"
            ) from exc

        raise ValueError(f"Unsupported EMBED_MODEL: {model}")
