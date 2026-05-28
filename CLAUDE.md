# CLAUDE.md — lfed-course-recommender

> This file tells Claude Code how to work with this project.
> Read it fully before writing any code, running any command, or modifying any file.

---

## Project overview

**lfed-course-recommender** is an AI-powered course recommendation and Q&A system built on
the Linux Foundation Training & Certification catalog (`training.linuxfoundation.org`).

Given a user's current skills and career goal, it retrieves relevant LF courses via RAG
and synthesises a personalised learning roadmap using an LLM.

Built by: Pratik Karanje (`github.com/pkaranje`)
Status: MVP — interview portfolio project, to be open-sourced later

---

## Architecture

This project follows the same layered architecture as the Library Management System:
`Routes → Services → Domain → Repositories → Infrastructure`

**No third-party LLM wrapper** — provider switching lives in `repositories/llm_client.py`
and `repositories/embed_client.py` using official SDKs only (ollama, openai,
google-generativeai, anthropic). The repository layer is the boundary between the app
and all external I/O — database, vector store, and LLM APIs alike.

```
app/
├── __init__.py
├── main.py              # FastAPI app, router includes, exception handlers, configure_logging()
├── core/
│   ├── __init__.py
│   ├── config.py        # Settings via pydantic-settings (LLM_MODEL, EMBED_MODEL, keys, Chroma)
│   ├── dependencies.py  # DI: get_vector_store, get_llm_client, get_embed_client, get_*_service
│   ├── middleware.py    # RequestLoggingMiddleware — request_id, structlog contextvars
│   └── logging.py      # configure_logging(), LoggerMixin, log_call decorator
├── domain/
│   ├── __init__.py      # Re-exports all validators, exceptions, constants
│   ├── course.py        # CourseCategory, validate_course_metadata(), exceptions
│   ├── query.py         # validate_user_query(), sanitise_input(), QueryTooLongError
│   └── recommendation.py # MAX_RESULTS, validate_recommendation(), RecommendationError
├── services/
│   ├── __init__.py      # BaseService(LoggerMixin)
│   ├── embedder.py      # EmbedderService — calls repositories/embed_client.py
│   ├── retriever.py     # RetrieverService — calls repositories/vector_store.py
│   ├── llm.py           # LLMService — calls repositories/llm_client.py
│   └── recommend.py     # RecommendService — orchestrates full RAG pipeline
├── repositories/
│   ├── __init__.py      # BaseRepository(LoggerMixin)
│   ├── vector_store.py  # VectorStoreRepository — ChromaDB CRUD
│   ├── llm_client.py    # LLMClient — official SDKs: ollama / openai / google / anthropic
│   └── embed_client.py  # EmbedClient — official SDKs: ollama / openai / google
├── ingestion/           # One-time data pipeline (not part of request path)
│   ├── __init__.py
│   ├── scraper.py       # httpx + BeautifulSoup, rate-limited, robots.txt aware
│   └── loader.py        # JSON → embed → upsert into ChromaDB
└── api/
    ├── __init__.py
    ├── schemas/
    │   ├── __init__.py
    │   ├── common.py    # ErrorDetail, HealthResponse
    │   ├── query.py     # RecommendRequest, RecommendResponse
    │   └── course.py    # CourseResult, CourseCard
    └── routes/
        ├── __init__.py
        ├── recommend.py # POST /recommend — full RAG pipeline
        ├── search.py    # GET /search — direct similarity search
        └── health.py    # GET /health
```

---

## Layer responsibilities

| Layer | Location | Responsibility |
|---|---|---|
| API | `app/api/` | FastAPI routes, Pydantic request/response schemas, HTTP concerns |
| Services | `app/services/` | Business logic, orchestration, no HTTP/DB awareness |
| Domain | `app/domain/` | Pure Python — validation rules, business exceptions, constants |
| Repositories | `app/repositories/` | All external I/O — ChromaDB, LLM APIs, embedding APIs |
| Ingestion | `app/ingestion/` | Offline pipeline — scrape → embed → store |
| Core | `app/core/` | Config, DI, middleware, logging — all cross-cutting infrastructure |

---

## Dependency direction

```
api/routes   → services     → domain              (pure, no I/O)
services     → repositories → chromadb            (vector store)
services     → repositories → ollama / openai     (LLM I/O)
             → repositories → ollama / openai /   (embed I/O)
                               google
all layers   → core/logging                       (observability)
all layers   → core/config                        (settings)
main.py      → core/middleware, core/dependencies  (wiring)
```

Nothing flows upward. Domain never imports from services. Repositories never import from services.

---

## Provider switching — official SDKs only

**No LiteLLM.** After the March 2026 supply chain attack (versions 1.82.7 and 1.82.8
delivered credential-harvesting malware), this project uses official SDKs only.
Provider switching lives entirely in `repositories/llm_client.py` and
`repositories/embed_client.py` — ~40 lines you own, zero third-party wrapper risk.

### Official SDKs

| Provider | LLM SDK | Embed SDK | Install |
|---|---|---|---|
| Ollama (default) | `ollama` | `ollama` | `uv add ollama` |
| OpenAI | `openai` | `openai` | `uv add openai` |
| Google | `google-generativeai` | `google-generativeai` | `uv add google-generativeai` |
| Anthropic | `anthropic` | n/a — use OpenAI embeddings | `uv add anthropic` |

### How provider switching works

```python
# repositories/llm_client.py
from app.core.config import settings

def complete(messages: list[dict]) -> str:
    if settings.LLM_MODEL.startswith("ollama/"):
        import ollama
        model = settings.LLM_MODEL.replace("ollama/", "")
        r = ollama.chat(model=model, messages=messages)
        return r["message"]["content"]

    elif settings.LLM_MODEL.startswith("gpt"):
        from openai import OpenAI
        r = OpenAI(api_key=settings.OPENAI_API_KEY).chat.completions.create(
            model=settings.LLM_MODEL, messages=messages, max_tokens=1000
        )
        return r.choices[0].message.content

    elif settings.LLM_MODEL.startswith("gemini/"):
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        r = genai.GenerativeModel(
            settings.LLM_MODEL.replace("gemini/", "")
        ).generate_content(messages[-1]["content"])
        return r.text

    elif settings.LLM_MODEL.startswith("anthropic/"):
        from anthropic import Anthropic
        r = Anthropic(api_key=settings.ANTHROPIC_API_KEY).messages.create(
            model=settings.LLM_MODEL.replace("anthropic/", ""),
            max_tokens=1000,
            messages=messages,
        )
        return r.content[0].text

    raise ValueError(f"Unsupported LLM_MODEL: {settings.LLM_MODEL}")
```

Same pattern in `repositories/embed_client.py` for embeddings.

### Supported model values

| Provider | LLM_MODEL | EMBED_MODEL | Key needed |
|---|---|---|---|
| Ollama (default) | `ollama/mistral` | `ollama/nomic-embed-text` | None |
| OpenAI | `gpt-4o-mini` | `text-embedding-3-small` | `OPENAI_API_KEY` |
| Google | `gemini/gemini-2.0-flash` | `gemini/text-embedding-004` | `GEMINI_API_KEY` |
| Anthropic | `anthropic/claude-haiku-4-5` | use `text-embedding-3-small` | `ANTHROPIC_API_KEY` + `OPENAI_API_KEY` |

### `.env` structure (local development)

```bash
# ── LLM (completion) ──────────────────────────────────────────
LLM_MODEL=ollama/mistral               # default — free, local, no key needed
# LLM_MODEL=gpt-4o-mini               # OpenAI
# LLM_MODEL=gemini/gemini-2.0-flash   # Google
# LLM_MODEL=anthropic/claude-haiku-4-5 # Anthropic

# ── Embeddings ────────────────────────────────────────────────
EMBED_MODEL=ollama/nomic-embed-text    # default — free, local, no key needed
# EMBED_MODEL=text-embedding-3-small  # OpenAI
# EMBED_MODEL=gemini/text-embedding-004 # Google

# ── Ollama ────────────────────────────────────────────────────
OLLAMA_HOST=http://localhost:11434     # local dev

# ── Optional provider keys ────────────────────────────────────
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=...
# ANTHROPIC_API_KEY=...

# ── ChromaDB (local dev) ──────────────────────────────────────
CHROMA_HOST=localhost
CHROMA_PORT=8080                       # external Docker port

# ── App settings ──────────────────────────────────────────────
TOP_K_RESULTS=5
MAX_QUERY_LENGTH=500
```

### `.env.docker` structure (Docker containers)

```bash
LLM_MODEL=ollama/mistral
EMBED_MODEL=ollama/nomic-embed-text
OLLAMA_HOST=http://host.docker.internal:11434   # reaches native Ollama from container
CHROMA_HOST=chromadb                            # Docker service name
CHROMA_PORT=8000                                # internal container port
TOP_K_RESULTS=5
MAX_QUERY_LENGTH=500
```

**Two env files — never mix them up:**

| File | Used by | Committed? |
|---|---|---|
| `.env` | `uv run` / `make dev` / local Python | ❌ gitignored |
| `.env.example` | Reference for new contributors | ✅ committed |
| `.env.docker` | Docker containers via `env_file` | ❌ gitignored |
| `.env.docker.example` | Reference for Docker setup | ✅ committed |

`app/core/config.py` reads these via `pydantic-settings`. All other modules import from `app.core.config`.
**Never read `os.environ` directly anywhere except `app/core/config.py`.**

---

## Docker setup (Apple Silicon Mac)

Ollama runs **natively on the Mac host** for Metal GPU acceleration.
Everything else runs in Docker containers.

```
Mac host (native):
  └── ollama serve  (port 11434, uses Metal GPU)

Docker Compose:
  ├── chromadb     (port 8080) → data persists to data/chroma_db/
  ├── backend      (port 8000) → calls host.docker.internal:11434 for Ollama
  └── frontend     (port 8501)
```

### ChromaDB volume — important

ChromaDB 1.5.9+ stores data at `/data` inside the container (not `/chroma/chroma`):

```yaml
chromadb:
  volumes:
    - ./data/chroma_db:/data    # ← /data not /chroma/chroma
```

### Dockerfile pattern — uv, not pip

Both Dockerfiles use `uv sync --frozen` — no `requirements.txt` needed:

```dockerfile
FROM python:3.12-slim

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# install exact versions from uv.lock — no dev deps in production
RUN uv sync --frozen --no-dev

# copy app code
COPY app/ ./app/

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- `--frozen` — uses exact versions from `uv.lock`, never re-resolves
- `--no-dev` — skips pytest, ruff, mypy — not needed in container
- No `requirements.txt` — `pyproject.toml` + `uv.lock` is the source of truth

Start order:
```bash
ollama serve          # terminal 1 — must be running before docker-compose
docker-compose up     # terminal 2
```

---

## Commands

All commands go through `make`. Run `make help` to see the full list.

### First-time setup
```bash
make ollama-pull      # pull mistral + nomic-embed-text (~4.3GB, one time)
make demo             # full stack: build + start + ingest (start here)
```

### Day-to-day development
```bash
make dev              # start FastAPI backend locally (hot reload)
make frontend-dev     # start Streamlit UI locally
make ollama-start     # start Ollama in background (if not already running)
```

### Data ingestion
```bash
make ingest           # scrape LF catalog + embed + load into ChromaDB (skips if done)
make ingest-force     # always re-run ingestion (e.g. after catalog updates)
```

### Docker
```bash
make build            # build all Docker images
make up               # start chromadb + backend + frontend
make run              # start services (alias for up)
make down             # stop all services
make logs             # tail backend logs
make logs-all         # tail all service logs
```

### Testing & quality
```bash
make test             # run all tests
make test-cov         # run tests with coverage report
make lint             # ruff lint check
make lint-fix         # auto-fix lint issues
make format           # ruff format
make typecheck        # mypy type check
```

### Cleanup
```bash
make clean            # remove __pycache__, .pyc files
make clean-all        # full reset — venv + docker volumes + chroma data + raw data
```

---

## Code conventions

### Python style
- Python 3.12+
- Type hints on all functions — no bare `def foo(x):`
- Pydantic models for all request/response schemas
- Synchronous FastAPI — no `async def` unless genuinely needed
- ChromaDB client is synchronous — keep it that way
- Docstrings on all public functions: one-line summary + Args + Returns
- Max line length: 88 (ruff default)
- `structlog` for all logging — never `print()`

### Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- No abbreviations except: `llm`, `rag`, `url`, `id`, `k`

### Imports order
```python
# 1. stdlib
import os
from typing import Optional

# 2. third-party
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# 3. local — always absolute from app/
from app.core.config import settings
from app.core.dependencies import get_vector_store
from app.services.recommend import RecommendService
from app.domain.query import validate_user_query
```

### Error handling
- Never bare `except:` — always catch specific exceptions
- Domain exceptions live in `app/domain/` — raise them from services
- FastAPI routes catch domain exceptions and return proper HTTP codes
- Scraper uses `tenacity` for retries with exponential backoff

### Logging pattern (same as Library project)
```python
from app.core.logging import LoggerMixin

class RecommendService(BaseService, LoggerMixin):
    def recommend(self, query: str) -> RecommendResponse:
        self.logger.info("recommendation_started", query_length=len(query))
        ...
        self.logger.info("recommendation_complete", courses_found=len(results))
```

---

## Security rules — never violate these

1. **No secrets in code** — all keys via `.env` + `pydantic-settings`
2. **`.env` is gitignored** — only `.env.example` is committed
3. **Scraper rules**:
   - Always check `robots.txt` before scraping any new path
   - Rate limit: 1 request/second, random jitter 0.5–1.5s via `tenacity`
   - User-Agent: `lfed-course-recommender/0.1 (open source; github.com/pkaranje/lfed-course-recommender)`
   - Only public pages — never scrape authenticated or login-gated content
4. **API security**:
   - All inputs validated via Pydantic — no raw strings passed to LLM
   - Query sanitisation in `app/domain/query.py` before any LLM call
   - Rate limiting on `/recommend` via `slowapi` (10 req/min per IP)
   - CORS: explicit origins only — never `allow_origins=["*"]`
5. **No PII logged** — user queries are not persisted, not logged at INFO+

---

## Data flow

### Ingestion (offline, run once)
```
training.linuxfoundation.org/full-catalog
    │  scraper.py — httpx, BeautifulSoup, 1 req/sec
    ▼
data/raw/courses.json
    [{ title, description, category, level, duration, url, cert_available }]
    │  loader.py — embed each description, upsert to ChromaDB
    ▼
ChromaDB collection: "lf_courses"
    documents:  course description text
    metadatas:  { title, category, level, url, cert_available }
    ids:        slugified URL
```

### Request path (online)
```
POST /recommend { skills, goal, category? }
    │  api/routes/recommend.py — Pydantic validation
    │  domain/query.py — sanitise, validate length
    ▼
RecommendService.recommend()
    │  EmbedderService.embed(query)
    │      → repositories/embed_client.py → ollama / openai / google
    │  RetrieverService.retrieve(embedding)
    │      → repositories/vector_store.py → ChromaDB top-5
    │  LLMService.generate(query, courses)
    │      → repositories/llm_client.py   → ollama / openai / google / anthropic
    ▼
RecommendResponse { roadmap, courses: [CourseCard] }
```

---

## RAG prompt structure

```python
SYSTEM_PROMPT = """You are a learning advisor for the Linux Foundation.
Given a learner's background and career goal, recommend a personalised learning path
using ONLY the courses provided in context.
Always cite course names and include their URLs.
Be specific, actionable, and honest about prerequisites."""

USER_PROMPT = """
Learner background: {skills}
Career goal: {goal}

Available courses from the LF catalog:
{formatted_courses}

Recommend a step-by-step learning path.
"""
```

---

## Project file structure

```
lfed-course-recommender/
├── CLAUDE.md                    ← you are here
├── LICENSE                      ← Apache 2.0
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
├── Makefile                     ← all commands live here
├── .env.example                 ← local dev reference (committed)
├── .env.docker.example          ← Docker reference (committed)
├── .gitignore                   ← includes: .env, .env.docker, data/chroma_db/
├── pyproject.toml               ← uv, dependencies, ruff + mypy config
├── uv.lock                      ← committed — exact versions for reproducible builds
├── docker-compose.yml
├── Dockerfile.backend           ← uses uv sync --frozen --no-dev
├── Dockerfile.frontend          ← uses uv sync --frozen --no-dev
│
├── app/                         ← main application (see Architecture above)
│   └── repositories/
│       ├── vector_store.py      ← ChromaDB CRUD
│       ├── llm_client.py        ← official SDKs: ollama/openai/google/anthropic
│       └── embed_client.py      ← official SDKs: ollama/openai/google
│
├── frontend/
│   └── app.py                   ← Streamlit UI
│
├── data/
│   ├── raw/                     ← scraped JSON (gitignored if > 10MB)
│   └── chroma_db/               ← vector store (always gitignored)
│
├── notebooks/
│   └── rag_eval.ipynb           ← retrieval quality exploration
│
├── tests/
│   ├── conftest.py
│   ├── test_scraper.py
│   ├── test_retriever.py
│   ├── test_recommend.py
│   └── test_llm.py
│
└── .github/
    ├── workflows/
    │   └── ci.yml               ← ruff + mypy + pytest on every PR
    └── ISSUE_TEMPLATE/
        ├── bug_report.md
        └── feature_request.md
```

---

## Data safety rules — never violate these

These rules protect the two data assets in this project: the scraped course catalog
(`data/raw/courses.json`) and the vector store (`data/chroma_db/`). Both are expensive
to regenerate — the scraper takes time and the embedding run costs API calls or GPU time.

### Protected paths — NEVER delete or overwrite without explicit user instruction

```
data/raw/courses.json       ← scraped catalog — hours to rebuild
data/chroma_db/             ← vector store — embedding run to rebuild
.env                        ← local dev credentials
.env.docker                 ← Docker credentials
```

### Hard rules

1. **Never run `rm -rf data/`** — not during cleanup, not during reset, not ever unless
   the user explicitly types "delete all data and start fresh"
2. **Never drop or reset the ChromaDB collection** — `collection.delete()` and
   `client.delete_collection()` are banned unless user explicitly asks to re-ingest
3. **Never truncate or overwrite `courses.json`** unless running `make ingest-force`
   and the user has explicitly confirmed
4. **`make clean` must never touch `data/`** — it only removes `__pycache__` and `.pyc`
5. **`make clean-all` must warn before deleting data** — print a confirmation message,
   do not auto-delete silently
6. **Docker volume removal is destructive** — never run `docker-compose down -v`
   without warning the user that ChromaDB data will be lost
7. **No git hooks that delete files** — pre-commit, pre-push hooks must never
   touch `data/`, `.env`, or any database files
8. **Ingestion is additive, not destructive** — `loader.py` must upsert, never
   drop-and-recreate the collection. Use `collection.upsert()` not `collection.add()`
   after checking for existing IDs

### Safe cleanup commands

```bash
make clean          ✅ safe  — only __pycache__ and .pyc
make down           ✅ safe  — stops containers, data volumes untouched
make down-all       ⚠️ warn  — removes volumes, ChromaDB data lost
make clean-all      ⚠️ warn  — full reset including data/ — must confirm
make ingest-force   ⚠️ warn  — re-embeds, overwrites courses.json
```

### If ChromaDB data is accidentally lost

```bash
make ingest-force   # re-scrapes + re-embeds everything
/verify-ingest      # confirm collection is repopulated
```

---

## What NOT to do

- Do not use LiteLLM or any third-party LLM wrapper — use official SDKs only
- Do not call ollama/openai/google/anthropic SDKs directly from services — always go through `repositories/llm_client.py` and `repositories/embed_client.py`
- Do not add a new provider without adding it to both `llm_client.py` and `embed_client.py`
- Do not use `async def` for ChromaDB calls — the client is synchronous
- Do not read `os.environ` directly — always go through `app/core/config.py`
- Do not add business logic to `api/routes/` — it belongs in `services/`
- Do not add I/O to `domain/` — it must stay pure Python
- Do not import from `services/` inside `repositories/` — dependency flows down only
- Do not log user queries at INFO level or above — privacy rule
- Do not use `allow_origins=["*"]` in CORS settings
- Do not scrape pages behind login or any authenticated endpoint
- Do not commit `.env`, `data/chroma_db/`, or any model weights
- Do not use `print()` for logging — use `structlog` via `LoggerMixin`
- Do not add new dependencies without updating `pyproject.toml` — run `uv add <package>`
- Do not run raw `uv run` or `python` commands — use `make` targets instead
- **Do not delete `data/raw/courses.json`** — expensive to regenerate
- **Do not delete or reset `data/chroma_db/`** — embedding run to rebuild
- **Do not run `docker-compose down -v`** without warning the user
- **Do not add git hooks that delete or modify data files**
- **Do not use `collection.delete()` or `client.delete_collection()`** without explicit user instruction
- **Do not make `make clean` touch `data/`** — clean is for Python cache only

---

*Last updated: May 2026 | Pratik Karanje | github.com/pkaranje/lfed-course-recommender*
