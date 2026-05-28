from pathlib import Path

RAW_DATA_PATH = Path("data/raw/courses.json")


def load(force: bool = False) -> None:
    """Load courses from JSON into ChromaDB via embed + upsert.

    Args:
        force: If True, re-embed and upsert even if collection is already populated.
    """
    raise NotImplementedError


def _format_document(course: dict) -> str:
    """Format a course dict into a text document for embedding.

    Args:
        course: Course metadata dict.

    Returns:
        Plain-text string combining title, description, and category.
    """
    raise NotImplementedError


def _slugify_url(url: str) -> str:
    """Convert a URL into a stable document ID.

    Args:
        url: Course page URL.

    Returns:
        URL-safe slug string.
    """
    raise NotImplementedError
