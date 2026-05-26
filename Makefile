# -------- Variables --------
VENV        := .venv
PYTHON      := $(VENV)/bin/python
PIP         := $(VENV)/bin/pip
UVICORN     := $(VENV)/bin/uvicorn
PYTEST      := $(VENV)/bin/pytest
RUFF        := ruff

APP         := app.main:app
PORT        := 8000

.DEFAULT_GOAL := help

# -------- Phony Targets --------
.PHONY: help venv install install-force dev ingest ingest-force \
        test lint lint-fix format typecheck clean clean-all \
        demo build run up down logs \
        ollama-pull ollama-start frontend-dev

# -------- Help --------
help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║           LF Course Navigator — Commands                 ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  make demo         ★ Full local demo: ollama + docker + ingest (start here)"
	@echo "  make run            Start all Docker services (if already built)"
	@echo "  make down           Stop Docker services"
	@echo "  make logs           Tail backend logs"
	@echo ""
	@echo "Ollama (local LLM — required for default config):"
	@echo "  make ollama-pull    Pull mistral + nomic-embed-text models (~4.3GB)"
	@echo "  make ollama-start   Start ollama server in background"
	@echo ""
	@echo "Data ingestion:"
	@echo "  make ingest         Scrape LF catalog + embed + load into ChromaDB"
	@echo "  make ingest-force   Re-run ingestion even if already done"
	@echo ""
	@echo "Local development:"
	@echo "  make install        Setup virtualenv & install dependencies"
	@echo "  make dev            Start FastAPI server locally"
	@echo "  make test           Run test suite"
	@echo "  make lint           Run ruff lint"
	@echo "  make lint-fix       Auto-fix lint issues"
	@echo "  make format         Format code with ruff"
	@echo "  make typecheck      Run mypy type checks"
	@echo "  make clean          Remove Python cache files"
	@echo "  make clean-all      Full reset (venv + docker volumes + chroma data)"
	@echo ""
	@echo "Docker:"
	@echo "  make build          Build Docker images"
	@echo "  make up             Start services with Docker Compose"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend-dev   Start Streamlit UI locally"
	@echo ""

# -------- Local Setup --------
venv:
	@[ -d $(VENV) ] || python3 -m venv $(VENV)

install: venv
	@test -f .env || cp .env.example .env
	@if [ ! -f "$(VENV)/.installed" ]; then \
		$(PIP) install --upgrade pip && \
		$(PIP) install -r requirements.txt && \
		touch $(VENV)/.installed; \
		echo "Dependencies installed"; \
	else \
		echo "Dependencies already installed (skip). Run 'make install-force' to reinstall"; \
	fi

install-force: venv
	@rm -f $(VENV)/.installed
	$(PIP) install --upgrade pip && \
	$(PIP) install -r requirements.txt && \
	touch $(VENV)/.installed

# -------- Ollama --------
ollama-pull:
	@echo ""
	@echo "► Pulling Ollama models (~4.3GB total, one-time download)..."
	@echo "  mistral:7b        — LLM for recommendations"
	@echo "  nomic-embed-text  — embeddings for RAG"
	@echo ""
	ollama pull mistral
	ollama pull nomic-embed-text
	@echo ""
	@echo "✓ Models ready"
	@echo ""

ollama-start:
	@echo "► Starting Ollama server in background..."
	@ollama serve &> /tmp/ollama.log &
	@sleep 2
	@echo "✓ Ollama running on http://localhost:11434"
	@echo "  Logs: tail -f /tmp/ollama.log"
	@echo ""

# -------- Local Dev --------
dev: install
	$(UVICORN) $(APP) --reload --host 0.0.0.0 --port $(PORT)

# -------- Ingestion --------
ingest: install
	@if [ ! -f "$(VENV)/.ingested" ]; then \
		echo "► Scraping LF catalog..."; \
		$(PYTHON) -m app.ingestion.scraper && \
		echo "► Embedding + loading into ChromaDB..."; \
		$(PYTHON) -m app.ingestion.loader && \
		touch $(VENV)/.ingested; \
		echo "✓ Ingestion complete"; \
	else \
		echo "Already ingested (skip). Run 'make ingest-force' to re-run"; \
	fi

ingest-force: install
	@rm -f $(VENV)/.ingested
	@echo "► Scraping LF catalog..."
	$(PYTHON) -m app.ingestion.scraper
	@echo "► Embedding + loading into ChromaDB..."
	$(PYTHON) -m app.ingestion.loader
	@touch $(VENV)/.ingested
	@echo "✓ Ingestion complete"

# -------- Tests --------
test: install
	$(PYTEST) -v

test-cov: install
	$(PYTEST) -v --cov=app --cov-report=term-missing

# -------- Dev Tools --------
lint:
	$(RUFF) check app tests

lint-fix:
	$(RUFF) check --fix app tests

format:
	$(RUFF) format app tests

typecheck:
	$(PYTHON) -m mypy app

# -------- Clean --------
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete

clean-all: clean
	@rm -rf $(VENV)
	@rm -rf data/chroma_db
	@rm -rf data/raw
	docker-compose down -v --remove-orphans
	@echo "✓ Full reset complete"

# -------- Docker --------
build:
	docker-compose build

up:
	docker-compose up -d
	@echo ""
	@echo "✓ Services started!"
	@echo "  API:      http://localhost:$(PORT)/api/v1"
	@echo "  Docs:     http://localhost:$(PORT)/docs"
	@echo "  ReDoc:    http://localhost:$(PORT)/redoc"
	@echo "  Frontend: http://localhost:8501"
	@echo "  ChromaDB: http://localhost:8080"
	@echo ""

run:
	docker-compose up -d
	@echo ""
	@echo "✓ Services started!"
	@echo "  API:      http://localhost:$(PORT)/api/v1"
	@echo "  Docs:     http://localhost:$(PORT)/docs"
	@echo "  Frontend: http://localhost:8501"
	@echo ""

down:
	docker-compose down

down-all:
	docker-compose down -v --remove-orphans

logs:
	docker-compose logs -f backend

logs-all:
	docker-compose logs -f

# -------- Frontend --------
frontend-dev:
	$(VENV)/bin/streamlit run frontend/app.py

# -------- Demo --------
demo:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║         LF Course Navigator — Full Demo                  ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Stack: FastAPI · ChromaDB · LiteLLM · Ollama · Streamlit · Docker"
	@echo ""
	@echo "► Step 1/5  Checking Ollama is installed..."
	@which ollama > /dev/null 2>&1 || (echo "✗ Ollama not found. Install: brew install ollama" && exit 1)
	@echo "  ✓ Ollama found"
	@echo ""
	@echo "► Step 2/5  Pulling models (skip if already pulled)..."
	@ollama list | grep -q "mistral" || ollama pull mistral
	@ollama list | grep -q "nomic-embed-text" || ollama pull nomic-embed-text
	@echo "  ✓ Models ready"
	@echo ""
	@echo "► Step 3/5  Preparing environment..."
	@test -f .env || cp .env.example .env
	@echo "  ✓ .env ready"
	@echo ""
	@echo "► Step 4/5  Building and starting Docker services..."
	@echo "  (Make sure ollama serve is running in another terminal)"
	@echo ""
	$(MAKE) build
	$(MAKE) up
	@echo "  Waiting for backend to be ready..."
	@until docker-compose exec -T backend curl -sf http://localhost:$(PORT)/api/v1/health > /dev/null 2>&1; do \
		printf '.'; sleep 3; \
	done
	@echo " ready!"
	@echo ""
	@echo "► Step 5/5  Running ingestion (scrape + embed LF catalog)..."
	@docker-compose exec -T backend sh -c \
		"python -m app.ingestion.scraper && python -m app.ingestion.loader"
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║                  Demo is ready!                          ║"
	@echo "╠══════════════════════════════════════════════════════════╣"
	@echo "║  Frontend   http://localhost:8501                        ║"
	@echo "║  API base   http://localhost:$(PORT)/api/v1                   ║"
	@echo "║  Swagger UI http://localhost:$(PORT)/docs                     ║"
	@echo "║  ReDoc      http://localhost:$(PORT)/redoc                    ║"
	@echo "║  ChromaDB   http://localhost:8080                        ║"
	@echo "╠══════════════════════════════════════════════════════════╣"
	@echo "║  Default LLM:    ollama/mistral (local, free)            ║"
	@echo "║  Default embed:  ollama/nomic-embed-text (local, free)   ║"
	@echo "║  Switch to OpenAI: edit LLM_MODEL in .env               ║"
	@echo "╠══════════════════════════════════════════════════════════╣"
	@echo "║  make logs           — tail backend logs                 ║"
	@echo "║  make ingest-force   — re-run ingestion                  ║"
	@echo "║  make down           — stop everything                   ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo ""
