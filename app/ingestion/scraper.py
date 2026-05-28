from collections.abc import Iterator

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://training.linuxfoundation.org"
CATALOG_URL = f"{BASE_URL}/full-catalog"
USER_AGENT = (
    "lfed-course-recommender/0.1 "
    "(open source; github.com/pkaranje/lfed-course-recommender)"
)
RATE_LIMIT_SECONDS = 1.0
JITTER_RANGE = (0.5, 1.5)


def scrape_catalog() -> Iterator[dict]:
    """Scrape the LF training catalog and yield course dicts.

    Yields:
        Course dict with title, description, category, level, duration, url, cert_available.
    """
    raise NotImplementedError


def _fetch(url: str, client: httpx.Client) -> BeautifulSoup:
    """Fetch a URL with rate limiting and return parsed HTML.

    Args:
        url: URL to fetch.
        client: Shared httpx client.

    Returns:
        Parsed BeautifulSoup document.
    """
    raise NotImplementedError


def _is_allowed(url: str) -> bool:
    """Check robots.txt before scraping a URL.

    Args:
        url: URL to check.

    Returns:
        True if scraping is permitted.
    """
    raise NotImplementedError
