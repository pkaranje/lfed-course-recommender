from app.core.config import settings
from app.repositories import BaseRepository


class EmbedClient(BaseRepository):
    def embed(self, text: str) -> list[float]:
        """Embed text using the configured embedding provider.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.

        Raises:
            ValueError: If EMBED_MODEL prefix is not supported.
        """
        if settings.EMBED_MODEL.startswith("ollama/"):
            import ollama
            model = settings.EMBED_MODEL.replace("ollama/", "")
            r = ollama.embeddings(model=model, prompt=text)
            return r["embedding"]

        elif settings.EMBED_MODEL.startswith("text-embedding"):
            from openai import OpenAI
            r = OpenAI(api_key=settings.OPENAI_API_KEY).embeddings.create(
                model=settings.EMBED_MODEL, input=text
            )
            return r.data[0].embedding

        elif settings.EMBED_MODEL.startswith("gemini/"):
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            r = genai.embed_content(
                model=settings.EMBED_MODEL.replace("gemini/", ""),
                content=text,
            )
            return r["embedding"]

        raise ValueError(f"Unsupported EMBED_MODEL: {settings.EMBED_MODEL}")
