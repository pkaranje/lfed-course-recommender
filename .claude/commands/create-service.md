Create the service for "$ARGUMENTS" in `app/services/$ARGUMENTS.py`.

Follow CLAUDE.md conventions:
- Class must extend BaseService and LoggerMixin
- No HTTP awareness — no FastAPI imports, no Request/Response objects
- No direct ChromaDB, ollama, openai, or any SDK calls — always go through
  repositories/llm_client.py, repositories/embed_client.py, repositories/vector_store.py
- Call domain validation functions before any I/O
- Use structlog via self.logger — never print()
- Raise domain exceptions from app/domain/ — never HTTPException
- Full type hints on all methods
- Docstrings: one-line summary + Args + Returns

Read existing services in app/services/ first to match the pattern exactly.
After creating, show me the file and confirm it is wired into app/core/dependencies.py.
