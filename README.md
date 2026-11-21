# lfed-course-recommender

AI-powered course recommendation and Q&A system built on the Linux Foundation Training & Certification catalog.

![CI](https://github.com/pkaranje/lfed-course-recommender/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-green)

Tell it your current skills and your career goal, and it retrieves the most relevant courses from the public catalog (RAG) and has an LLM write a personalised, step-by-step learning roadmap that cites the course names and URLs.

> Independent portfolio project. It is not affiliated with or endorsed by the Linux Foundation.

## How it works

```
Offline ingestion:
  training.linuxfoundation.org catalog -> scraper (rate-limited, robots.txt aware)
    -> courses.json -> embed each description -> ChromaDB

Request path:
  POST /recommend { skills, goal, category? }
    -> validate and sanitise input
    -> embed the query -> retrieve top courses from ChromaDB
    -> LLM writes the roadmap using only the retrieved courses
    -> { roadmap, courses }
```

## Stack

| Part | Technology |
| --- | --- |
| API | FastAPI, Pydantic, slowapi rate limiting |
| UI | Streamlit |
| Vector store | ChromaDB |
| LLM and embeddings | Ollama (default, runs locally), OpenAI, Google, Anthropic via their official SDKs |
| Ingestion | httpx, BeautifulSoup, tenacity |
| Tooling | uv, Docker Compose, ruff, mypy, pytest, GitHub Actions CI |

Provider switching is a configuration change (`LLM_MODEL`, `EMBED_MODEL`) handled in one small repository layer. No third-party LLM wrapper is used.

## Quickstart

Requires Docker and [Ollama](https://ollama.com) running on the host.

```bash
make ollama-pull   # one-time: pulls mistral and nomic-embed-text (about 4.3 GB)
make demo          # builds the images, starts all services, runs ingestion
```

- UI: http://localhost:8501
- API: http://localhost:8000 (`POST /recommend`, `GET /search`, `GET /health`)

Run `make help` for all targets (dev servers, ingestion, tests, lint, type checking, Docker).

To use a hosted model instead of Ollama, set `LLM_MODEL`, `EMBED_MODEL` and the matching API key in `.env`. See `.env.example`.

## Architecture

Layered: routes -> services -> domain (pure validation) -> repositories (ChromaDB, LLM and embedding APIs) -> infrastructure. Dependencies only point downward, and all external I/O lives in the repository layer. Conventions are documented in `CLAUDE.md`.

## Responsible scraping and privacy

- The scraper checks `robots.txt`, rate-limits itself, and reads public pages only.
- User queries are not persisted or logged at INFO level or above.
- Inputs are validated before they reach the LLM.

## Status

MVP. Contributions are welcome: see `CONTRIBUTING.md`. Licensed under Apache 2.0.
