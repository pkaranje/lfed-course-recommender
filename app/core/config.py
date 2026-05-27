from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_MODEL: str = "ollama/mistral"
    EMBED_MODEL: str = "ollama/nomic-embed-text"

    OLLAMA_HOST: str = "http://localhost:11434"

    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000

    TOP_K_RESULTS: int = 5
    MAX_QUERY_LENGTH: int = 500

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
