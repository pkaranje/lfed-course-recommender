import argparse
import json
import re
import sys
from pathlib import Path

import structlog

from app.core.logging import configure_logging
from app.repositories.embed_client import EmbedClient
from app.repositories.vector_store import VectorStoreRepository

RAW_DATA_PATH = Path("data/raw/courses.json")

logger = structlog.get_logger(__name__)


def _slugify_url(url: str) -> str:
    """Convert a URL into a stable document ID.

    Args:
        url: Course page URL.

    Returns:
        URL-safe slug string using re.sub.
    """
    return re.sub(r"[^a-zA-Z0-9]+", "-", url).strip("-")


def _format_document(course: dict) -> str:
    """Format a course dict into a text document for embedding.

    Args:
        course: Course metadata dict.

    Returns:
        Plain-text string combining title, description, and category.
    """
    parts = [course.get("title", ""), course.get("description", "")]
    if course.get("category"):
        parts.append(f"Category: {course['category']}")
    if course.get("level"):
        parts.append(f"Level: {course['level']}")
    return " | ".join(p for p in parts if p)


def load(force: bool = False) -> None:
    """Load courses from JSON into ChromaDB via embed + upsert.

    Args:
        force: If True, re-embed and upsert even if already in ChromaDB.
    """
    log = structlog.get_logger(__name__)

    if not RAW_DATA_PATH.exists():
        log.error("raw_data_missing", path=str(RAW_DATA_PATH))
        raise FileNotFoundError(
            f"{RAW_DATA_PATH} not found. Run app.ingestion.scraper first."
        )

    courses: list[dict] = json.loads(RAW_DATA_PATH.read_text())
    log.info("courses_loaded_from_json", count=len(courses))

    embed_client = EmbedClient()
    vector_store = VectorStoreRepository()

    # Build set of existing IDs to skip unless --force
    existing_ids: set[str] = set()
    if not force:
        try:
            collection = vector_store.get_or_create_collection("lf_courses")
            result = collection.get(include=[])
            existing_ids = set(result.get("ids", []))
            log.info("existing_ids_fetched", count=len(existing_ids))
        except Exception as exc:
            log.warning("existing_ids_fetch_failed", error=str(exc))

    upserted = 0
    skipped = 0

    for i, course in enumerate(courses):
        doc_id = _slugify_url(course.get("url", f"course-{i}"))

        if not force and doc_id in existing_ids:
            skipped += 1
            continue

        document = _format_document(course)
        if not document.strip():
            log.warning("empty_document_skipped", index=i, title=course.get("title"))
            continue

        try:
            embedding = embed_client.embed(document)
        except Exception as exc:
            log.warning(
                "embed_failed", index=i, title=course.get("title"), error=str(exc)
            )
            continue

        metadata = {
            "title": course.get("title", ""),
            "category": course.get("category", ""),
            "level": course.get("level", ""),
            "url": course.get("url", ""),
            "cert_available": course.get("cert_available", False),
        }

        try:
            vector_store.upsert(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id],
                embeddings=[embedding],
            )
            upserted += 1
        except Exception as exc:
            log.warning(
                "upsert_failed", index=i, title=course.get("title"), error=str(exc)
            )
            continue

        if (i + 1) % 10 == 0:
            log.info(
                "loader_progress", processed=i + 1, upserted=upserted, skipped=skipped
            )

    log.info(
        "loader_complete",
        total=len(courses),
        upserted=upserted,
        skipped=skipped,
    )


if __name__ == "__main__":
    configure_logging()

    parser = argparse.ArgumentParser(description="Load LF courses into ChromaDB")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-embed and upsert all courses, even if already in ChromaDB",
    )
    args = parser.parse_args()

    log = structlog.get_logger(__name__)
    log.info("ingestion_loader_started", force=args.force)

    try:
        load(force=args.force)
    except FileNotFoundError as exc:
        log.error("loader_failed", error=str(exc))
        sys.exit(1)
    except Exception as exc:
        log.error("loader_failed", error=str(exc))
        sys.exit(1)
