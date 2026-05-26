# lfed-course-recommender — Claude Code Prompts

## How to use

1. Place `CLAUDE.md`, `Makefile`, and `.claude/` folder in your repo root
2. Open Claude Code: `claude` in the project directory
3. Run prompts **in order** — each builds on the previous
4. Use `/clear` between prompts to reset context and save tokens
5. CLAUDE.md is loaded automatically — prompts stay short because of it
6. Verify the checklist at the end of each prompt before moving on

## Slash commands (token savers)

| Command | What it does | Tokens saved |
|---|---|---|
| `/create-domain <name>` | Domain module — enums, validators, exceptions | ~150 |
| `/create-service <name>` | Service class with LoggerMixin | ~150 |
| `/create-schema <name>` | Pydantic request/response schemas | ~120 |
| `/create-route <name>` | FastAPI route with DI + error mapping | ~130 |
| `/create-test <name>` | pytest file with mocks | ~120 |
| `/verify-ingest` | Run ingestion + verify ChromaDB populated | ~100 |
| `/health-check` | Check all 4 services are running | ~80 |

## Token budget

| Approach | Tokens/prompt | 12 prompts |
|---|---|---|
| Without CLAUDE.md, verbose | ~900 | ~10,800 |
| With CLAUDE.md, verbose | ~500 | ~6,000 |
| With CLAUDE.md + slash commands | ~150 | ~1,800 |

---

# Prompt 1 — Repo scaffold

> Use this prompt once. Takes ~5 mins. Run `/clear` after.

```
Read CLAUDE.md fully before starting.

Note: .gitignore, pyproject.toml, and uv.lock are already committed.
Do not recreate them. Start from step 1 below.

Create the complete project scaffold for lfed-course-recommender:

1. Community files (root):
   - LICENSE (Apache 2.0, copyright Pratik Karanje 2026)
   - README.md (project title, one-line description, badges placeholder, quickstart: make demo)
   - CONTRIBUTING.md (how to fork, branch, PR, upstream)
   - CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
   - SECURITY.md (vulnerability disclosure — email only, no public issues)
   - CHANGELOG.md (## [0.1.0] — Unreleased section)

2. Config files (root):
   - .env.example (full contents from the Provider switching section in CLAUDE.md — Ollama as default)

3. Full app/ skeleton — create all __init__.py files and empty module stubs:
   app/__init__.py, app/main.py, app/config.py, app/dependencies.py, app/middleware.py
   app/core/__init__.py, app/core/logging.py
   app/domain/__init__.py, app/domain/course.py, app/domain/query.py, app/domain/recommendation.py
   app/services/__init__.py, app/services/embedder.py, app/services/retriever.py
   app/services/llm.py, app/services/recommend.py
   app/repositories/__init__.py, app/repositories/vector_store.py
   app/repositories/llm_client.py, app/repositories/embed_client.py
   app/ingestion/__init__.py, app/ingestion/scraper.py, app/ingestion/loader.py
   app/api/__init__.py
   app/api/schemas/__init__.py, app/api/schemas/common.py, app/api/schemas/query.py, app/api/schemas/course.py
   app/api/routes/__init__.py, app/api/routes/health.py, app/api/routes/recommend.py, app/api/routes/search.py

4. Other directories:
   - frontend/app.py (empty stub)
   - data/raw/.gitkeep
   - data/chroma_db/.gitkeep (this dir must be in .gitignore)
   - notebooks/rag_eval.ipynb (empty notebook)
   - tests/__init__.py, tests/conftest.py (empty for now)
   - tests/test_scraper.py, tests/test_retriever.py, tests/test_recommend.py, tests/test_llm.py (empty stubs)
   - .github/workflows/ci.yml (ruff check + mypy + pytest on push/PR to main)
   - .github/ISSUE_TEMPLATE/bug_report.md
   - .github/ISSUE_TEMPLATE/feature_request.md

Do not implement any logic yet — stubs and empty files only.
After creating all files, run: find . -name "*.py" | grep -v ".venv" | sort
```

**Checklist before `/clear`:**
- [ ] `find app -name "*.py" | grep -v .venv | wc -l` returns 20+
- [ ] `.env.example` has `LLM_MODEL=ollama/mistral` as default
- [ ] `.gitignore` includes `data/chroma_db/` and `.env`
- [ ] `pyproject.toml` has `requires-python = ">=3.12"`
- [ ] `uv.lock` exists and is committed

---

# Prompt 2 — Docker + config

> Run after Prompt 1. Takes ~5 mins. Run `/clear` after.

```
Read CLAUDE.md fully before starting.

Implement the Docker setup and app configuration:

1. docker-compose.yml with three services:
   - chromadb: image chromadb/chroma:latest, port 8080:8000, volume data/chroma_db:/chroma/chroma
   - backend: build Dockerfile.backend, port 8000:8000, env_file .env,
     depends_on chromadb, volume ./app:/app/app (hot reload)
   - frontend: build Dockerfile.frontend, port 8501:8501, env_file .env,
     depends_on backend

2. Dockerfile.backend:
   - FROM python:3.12-slim
   - COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
   - WORKDIR /app
   - COPY pyproject.toml uv.lock ./
   - RUN uv sync --frozen --no-dev
   - COPY app/ ./app/
   - CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

3. Dockerfile.frontend:
   - FROM python:3.12-slim
   - COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
   - WORKDIR /app
   - COPY pyproject.toml uv.lock ./
   - RUN uv sync --frozen --no-dev
   - COPY frontend/ ./frontend/
   - CMD ["uv", "run", "streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

4. app/config.py using pydantic-settings:
   - Class Settings(BaseSettings)
   - Fields: LLM_MODEL, EMBED_MODEL, OLLAMA_API_BASE, CHROMA_HOST, CHROMA_PORT,
     TOP_K_RESULTS (default 5), MAX_QUERY_LENGTH (default 500)
   - Optional fields: OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY
   - model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
   - settings = Settings() singleton at module level

5. app/core/logging.py:
   - configure_logging() — structlog setup with JSON renderer in prod, console in dev
   - LoggerMixin class — adds self.logger = structlog.get_logger(class_name)
   - log_call decorator — logs function entry/exit with timing

6. app/middleware.py:
   - RequestLoggingMiddleware — adds request_id (UUID) to structlog context vars
   - Logs method, path, status_code, duration_ms on every request

7. app/main.py:
   - FastAPI app with title, version, lifespan
   - Mount all routers from app/api/routes/
   - Add RequestLoggingMiddleware
   - CORS with explicit origins from settings (localhost:8501 for Streamlit)
   - Include /api/v1 prefix on all routes

After implementing, run: make build
Show me the docker-compose output — it must build without errors.
```

**Checklist before `/clear`:**
- [ ] `make build` completes without errors
- [ ] `docker-compose config` shows all 3 services
- [ ] `app/config.py` has `LLM_MODEL` defaulting to `ollama/mistral`
- [ ] `app/main.py` imports and mounts all routers

---

# Prompt 3 — Domain layer

> Run after Prompt 2. Takes ~5 mins. Run `/clear` after.

```
Read CLAUDE.md fully before starting.

Implement the full domain layer — pure Python, no I/O anywhere in this layer.

1. app/domain/course.py:
   - CourseCategory enum: cloud_containers, ai_ml, devops, cybersecurity, linux,
     networking, blockchain, iot, web_dev, systems_engineering, open_source
   - CourseLevel enum: beginner, intermediate, advanced
   - CourseMetadata dataclass: title, description, category, level, url, cert_available
   - validate_course_metadata(data: dict) -> CourseMetadata — raises InvalidCourseError
   - InvalidCourseError(ValueError) with descriptive message

2. app/domain/query.py:
   - MAX_QUERY_LENGTH = 500 (from settings)
   - sanitise_input(text: str) -> str — strip, collapse whitespace, remove control chars
   - validate_user_query(query: str) -> str — raises QueryTooLongError, QueryEmptyError
   - QueryTooLongError(ValueError), QueryEmptyError(ValueError)

3. app/domain/recommendation.py:
   - MAX_RESULTS = 5
   - MIN_RESULTS = 1
   - validate_top_k(k: int) -> int — raises InvalidTopKError if out of range
   - InvalidTopKError(ValueError)

4. app/domain/__init__.py — re-export all enums, dataclasses, validators, exceptions

After implementing, run:
  python3 -c "from app.domain import CourseCategory, validate_user_query; print('domain OK')"
```

**Checklist before `/clear`:**
- [ ] Import check passes
- [ ] Domain files have zero imports from `app.services`, `app.repositories`, or any I/O library
- [ ] All validators raise exceptions, never return bool

---

# Prompt 4 — Repository layer

> Run after Prompt 3. Takes ~10 mins. Run `/clear` after.

```
Read CLAUDE.md fully before starting.

Implement the full repository layer — all external I/O lives here.
Three files: vector_store.py, llm_client.py, embed_client.py.

1. app/repositories/vector_store.py — VectorStoreRepository(BaseRepository, LoggerMixin):
   - __init__(self, settings: Settings) — creates chromadb.HttpClient
   - get_or_create_collection(name: str) -> Collection
   - upsert(documents: list[str], metadatas: list[dict], ids: list[str]) -> None
   - query(embedding: list[float], n_results: int, where: dict | None) -> list[dict]
     Returns list of: {title, description, category, level, url, cert_available, distance}
   - count() -> int — number of documents in collection
   - All methods log entry/exit via self.logger
   - Raises RepositoryError on ChromaDB failures

2. app/repositories/llm_client.py — LLMClient(BaseRepository, LoggerMixin):
   - complete(messages: list[dict]) -> str
   - Switches on settings.LLM_MODEL prefix:
       "ollama/"    → import ollama; ollama.chat(model=..., messages=...)
       "gpt"        → from openai import OpenAI; client.chat.completions.create(...)
       "gemini/"    → import google.generativeai as genai; GenerativeModel(...).generate_content(...)
       "anthropic/" → from anthropic import Anthropic; client.messages.create(...)
   - Raises LLMClientError(RepositoryError) on any SDK failure
   - Logs provider, model, and response length on success
   - OLLAMA_HOST from settings for ollama SDK host config

3. app/repositories/embed_client.py — EmbedClient(BaseRepository, LoggerMixin):
   - embed(text: str) -> list[float]
   - Switches on settings.EMBED_MODEL prefix:
       "ollama/"               → ollama.embeddings(model=..., prompt=text)
       "text-embedding"        → OpenAI embeddings API
       "gemini/"               → google.generativeai embed_content
   - Raises EmbedClientError(RepositoryError) on any SDK failure
   - Logs provider, model, and embedding dimension on success

4. app/repositories/__init__.py — export all three classes and their exceptions

5. app/dependencies.py — add getters:
   - get_vector_store() -> VectorStoreRepository
   - get_llm_client() -> LLMClient
   - get_embed_client() -> EmbedClient
   (leave service getters as stubs for now)

After implementing:
  python3 -c "from app.repositories import VectorStoreRepository, LLMClient, EmbedClient; print('repos OK')"
```

**Checklist before `/clear`:**
- [ ] Import check passes
- [ ] `LLMClient` and `EmbedClient` have zero business logic — switching only
- [ ] All methods have type hints and docstrings
- [ ] No SDK imported at module level — import inside each branch only (lazy imports)

---

# Prompt 5 — Ingestion pipeline

> Run after Prompt 4. Ollama must be running. Takes ~10 mins (includes scraping). Run `/clear` after.

```
Read CLAUDE.md fully before starting.

Implement the ingestion pipeline — this runs once to populate ChromaDB.

1. app/ingestion/scraper.py:
   - Scrape https://training.linuxfoundation.org/full-catalog/
   - Use httpx with headers: User-Agent: lfed-course-recommender/0.1 (open source; github.com/pkaranje/lfed-course-recommender)
   - Check robots.txt first — only scrape allowed paths
   - Rate limit: sleep random 0.5–1.5s between requests using tenacity
   - Extract per course: title, description, category, level, duration, url, cert_available
   - Save to data/raw/courses.json as list of dicts
   - Log progress every 10 courses via structlog
   - ScraperError(Exception) for unrecoverable failures

2. app/ingestion/loader.py:
   - Read data/raw/courses.json
   - For each course: embed description using litellm.embedding(model=settings.EMBED_MODEL, input=[description])
   - Upsert into ChromaDB via VectorStoreRepository
   - id = slugified URL (use re.sub to replace non-alphanumeric with -)
   - Log progress every 10 courses
   - Skip courses already in ChromaDB (check by id) unless --force flag passed

3. Both files runnable as modules:
   python3 -m app.ingestion.scraper   # produces data/raw/courses.json
   python3 -m app.ingestion.loader    # populates ChromaDB

After implementing, run:
  make ingest
Then run:
  /verify-ingest
Do not proceed until ChromaDB has courses loaded.
```

**Checklist before `/clear`:**
- [ ] `data/raw/courses.json` exists and has 50+ courses
- [ ] `/verify-ingest` confirms ChromaDB count > 0
- [ ] Test query returns relevant LF courses

---

# Prompt 6 — Services layer

> Run after Prompt 5. Takes ~10 mins. Run `/clear` after.

```
Read CLAUDE.md fully before starting.

Implement all four services. All extend BaseService and LoggerMixin.
Read app/repositories/ fully before starting — services call repositories only.

1. app/services/embedder.py — EmbedderService:
   - embed(text: str) -> list[float]
   - Calls domain validate_user_query(text) first
   - Calls EmbedClient.embed(text) from repositories/embed_client.py
   - Logs embedding dimension on success
   - Raises EmbeddingError(ServiceError) wrapping EmbedClientError

2. app/services/retriever.py — RetrieverService:
   - retrieve(query: str, top_k: int = 5, category: str | None = None) -> list[dict]
   - Calls EmbedderService.embed() to get query embedding
   - Calls VectorStoreRepository.query() with optional category filter
   - Validates top_k via domain validate_top_k()
   - Logs retrieval count and top course title
   - Raises RetrieverError(ServiceError) if no results found

3. app/services/llm.py — LLMService:
   - generate(query: str, courses: list[dict]) -> str
   - Builds system + user prompt from CLAUDE.md RAG prompt structure
   - Calls LLMClient.complete(messages) from repositories/llm_client.py
   - Logs model used and response length on success
   - Raises LLMError(ServiceError) wrapping LLMClientError

4. app/services/recommend.py — RecommendService:
   - recommend(skills: str, goal: str, category: str | None = None) -> RecommendResponse
   - Orchestrates: validate → retrieve → generate
   - Calls validate_user_query on both skills and goal
   - Calls RetrieverService.retrieve()
   - Calls LLMService.generate()
   - Logs full pipeline timing end-to-end

5. Update app/dependencies.py with getters for all services via FastAPI Depends()

After implementing, test the full pipeline end-to-end:
  python3 -c "
from app.services.recommend import RecommendService
svc = RecommendService()
result = svc.recommend(skills='Python, Docker', goal='Learn Kubernetes')
print(result)
"
```

**Checklist before `/clear`:**
- [ ] Pipeline test runs end-to-end without errors
- [ ] LLM response includes at least one LF course name and URL
- [ ] No SDK imports (ollama, openai, google, anthropic) anywhere in services — only repository imports
- [ ] No chromadb imports in services — only repository imports

---

# Prompt 7 — API schemas

> Run after Prompt 6. Takes ~5 mins. Run `/clear` after.

```
Read CLAUDE.md fully before starting.
Read app/domain/ and app/services/ before writing schemas.

Implement all Pydantic v2 schemas:

1. app/api/schemas/common.py:
   - ErrorDetail: code: str, message: str, field: str | None = None
   - ErrorResponse: error: ErrorDetail
   - HealthResponse: status: Literal["ok"], version: str, timestamp: datetime

2. app/api/schemas/query.py:
   - RecommendRequest: skills: str, goal: str, category: CourseCategory | None, top_k: int = 5
     Add @field_validator on skills and goal — min 3 chars, max 500 chars
   - RecommendResponse: roadmap: str, courses: list[CourseCard], model_used: str

3. app/api/schemas/course.py:
   - CourseCard: title: str, url: str, category: CourseCategory, level: CourseLevel,
     cert_available: bool, relevance_score: float | None = None

Use Pydantic v2 ConfigDict. No bare dict — always typed models.
After implementing:
  python3 -c "from app.api.schemas import RecommendRequest, RecommendResponse; print('schemas OK')"
```

**Checklist before `/clear`:**
- [ ] Import check passes
- [ ] `RecommendRequest` rejects empty skills/goal
- [ ] All schemas use Pydantic v2 syntax

---

# Prompt 8 — API routes

> Run after Prompt 7. Takes ~5 mins. Run `/clear` after.

```
Read CLAUDE.md fully before starting.
Read app/api/schemas/, app/services/, app/domain/ before writing routes.

Implement all API routes:

1. app/api/routes/health.py:
   - GET /health → HealthResponse
   - Returns {"status": "ok", "version": "0.1.0", "timestamp": now}

2. app/api/routes/recommend.py:
   - POST /recommend → RecommendResponse
   - Request body: RecommendRequest
   - Inject RecommendService via Depends()
   - Add slowapi rate limiter: 10/minute per IP
   - Map domain exceptions to HTTP codes:
       QueryTooLongError → 422
       QueryEmptyError → 422
       RetrieverError → 404
       LLMError → 503
       Any other → 500

3. app/api/routes/search.py:
   - GET /search?q=<query>&category=<category>&top_k=<int> → list[CourseCard]
   - Inject RetrieverService via Depends()
   - No rate limiter on search (read-only)
   - Map domain exceptions to HTTP codes

4. Register all routers in app/main.py with prefix /api/v1

After implementing, run:
  make up
  curl -s http://localhost:8000/api/v1/health | python3 -m json.tool
  curl -s -X POST http://localhost:8000/api/v1/recommend \
    -H "Content-Type: application/json" \
    -d '{"skills": "Python, Docker", "goal": "Learn Kubernetes"}' | python3 -m json.tool

Both must return valid JSON responses.
```

**Checklist before `/clear`:**
- [ ] `GET /health` returns 200
- [ ] `POST /recommend` returns roadmap + courses
- [ ] Swagger UI at http://localhost:8000/docs shows all endpoints
- [ ] Rate limiter returns 429 after 10 rapid requests

---

# Prompt 9 — Streamlit frontend

> Run after Prompt 8. Backend must be running. Takes ~10 mins. Run `/clear` after.

```
Read CLAUDE.md fully before starting.
The backend is running at http://localhost:8000/api/v1.

Implement frontend/app.py as a Streamlit UI:

Layout:
- Page title: "LF Education Course Navigator"
- Sidebar: model info (LLM_MODEL, EMBED_MODEL from .env), link to API docs
- Main area:
    1. Text area: "Your current skills" (placeholder: "e.g. Python, Docker, Linux")
    2. Text area: "Your career goal" (placeholder: "e.g. Become a Kubernetes engineer")
    3. Selectbox: "Filter by category" (all CourseCategory values + "All categories")
    4. Slider: "Number of results" (1–10, default 5)
    5. Button: "Find my learning path"
    6. On submit:
       - POST to http://localhost:8000/api/v1/recommend
       - Show spinner while waiting
       - Display roadmap as markdown
       - Display each CourseCard as an expander with title, level, cert badge, URL button
    7. Error handling: show st.error() on API failures

Style:
- Use st.set_page_config(layout="wide")
- Show LF Education branding in header
- Green cert badge if cert_available, gray if not

After implementing, run:
  make frontend-dev
Visit http://localhost:8501 and test a full recommendation flow.
Show me a screenshot description of the working UI.
```

**Checklist before `/clear`:**
- [ ] Streamlit starts without errors
- [ ] Full recommendation flow works end-to-end
- [ ] Error state shows gracefully when backend is down

---

# Prompt 10 — Tests

> Run after Prompt 9. Takes ~10 mins. Run `/clear` after.

```
Read CLAUDE.md fully before starting.
Read all files in app/ before writing tests — match exact function signatures.

1. tests/conftest.py:
   - Fixture: mock_settings — returns Settings with test values
   - Fixture: mock_chroma_collection — MagicMock with .query(), .upsert(), .count()
   - Fixture: mock_litellm_completion — patches litellm.completion
   - Fixture: mock_litellm_embedding — patches litellm.embedding, returns 384-dim vector
   - Fixture: test_client — FastAPI TestClient with mocked dependencies

2. /create-test scraper
3. /create-test retriever
4. /create-test recommend
5. /create-test llm

After all tests written, run:
  make test-cov

Target: 70%+ coverage on app/services/ and app/domain/
Show me the coverage report output.
```

**Checklist before `/clear`:**
- [ ] `make test` passes with 0 failures
- [ ] No real API calls in any test — all litellm + ChromaDB calls mocked
- [ ] Coverage ≥ 70% on services and domain

---

# Prompt 11 — CI + community files

> Run after Prompt 10. Takes ~5 mins. Final prompt.

```
Read CLAUDE.md fully before starting.

1. .github/workflows/ci.yml — complete implementation:
   - Trigger: push and pull_request to main
   - Job: test
     - runs-on: ubuntu-latest
     - python-version: "3.12"
     - Steps: checkout, install uv, uv sync --frozen --dev,
       ruff check app tests, mypy app, pytest tests/ --cov=app
   - No Ollama or ChromaDB in CI — all external calls are mocked in tests

2. README.md — fill in properly:
   - Badges: Python 3.12, License Apache 2.0, CI status
   - One-paragraph description
   - Architecture diagram (ASCII)
   - Quickstart: Prerequisites (ollama, docker), then make demo
   - Provider switching table (Ollama/OpenAI/Gemini/Anthropic)
   - Contributing section pointing to CONTRIBUTING.md

3. Final checks — run all of these and show output:
   make lint
   make typecheck
   make test
   make health-check

Everything must pass before tagging v0.1.0.
```

**Final checklist:**
- [ ] `make lint` — 0 errors
- [ ] `make typecheck` — 0 errors
- [ ] `make test` — 0 failures
- [ ] `/health-check` — all 4 services green
- [ ] `POST /recommend` returns a full roadmap with LF course URLs
- [ ] README has working quickstart
- [ ] `git tag v0.1.0` — ready to push

---

## Quick reference — prompt order

```
Prompt 1  →  Scaffold          (repo structure, community files, stubs)
Prompt 2  →  Docker + config   (compose, Dockerfiles, config.py, logging, main.py)
Prompt 3  →  Domain            (enums, validators, exceptions — pure Python)
Prompt 4  →  Repository        (ChromaDB access layer)
Prompt 5  →  Ingestion         (scraper + loader — run make ingest after)
Prompt 6  →  Services          (embedder, retriever, llm, recommend)
Prompt 7  →  Schemas           (Pydantic request/response models)
Prompt 8  →  Routes            (FastAPI endpoints, rate limiting, error mapping)
Prompt 9  →  Frontend          (Streamlit UI)
Prompt 10 →  Tests             (pytest + mocks + coverage)
Prompt 11 →  CI + README       (GitHub Actions, final checks, v0.1.0 tag)
```

*Last updated: May 2026 | Pratik Karanje | github.com/pkaranje/lfed-course-recommender*
