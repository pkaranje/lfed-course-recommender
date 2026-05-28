import json
import random
import time
import urllib.robotparser
from pathlib import Path

import httpx
import structlog
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.logging import configure_logging

BASE_URL = "https://training.linuxfoundation.org"
CATALOG_URL = f"{BASE_URL}/full-catalog/"
ROBOTS_URL = f"{BASE_URL}/robots.txt"
USER_AGENT = (
    "lfed-course-recommender/0.1 "
    "(open source; github.com/pkaranje/lfed-course-recommender)"
)
JITTER_RANGE = (0.5, 1.5)
RAW_DATA_PATH = Path("data/raw/courses.json")

logger = structlog.get_logger(__name__)


class ScraperError(Exception):
    pass


def _build_client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
        timeout=30.0,
    )


def _is_allowed(url: str, client: httpx.Client) -> bool:
    """Check robots.txt to verify the URL is allowed to scrape.

    Args:
        url: URL to check.
        client: Shared httpx client.

    Returns:
        True if scraping is permitted.
    """
    rp = urllib.robotparser.RobotFileParser()
    try:
        resp = client.get(ROBOTS_URL)
        rp.parse(resp.text.splitlines())
    except Exception:
        return True
    return rp.can_fetch(USER_AGENT, url)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _fetch(url: str, client: httpx.Client) -> BeautifulSoup:
    """Fetch a URL with rate-limit jitter and return parsed HTML.

    Args:
        url: URL to fetch.
        client: Shared httpx client.

    Returns:
        Parsed BeautifulSoup document.
    """
    time.sleep(random.uniform(*JITTER_RANGE))
    resp = client.get(url)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def _extract_course(card: BeautifulSoup) -> dict | None:
    """Extract course fields from an lf-owl-card element.

    The LF catalog uses these span classes inside each <a class="product-card">:
      - .lf-owl-card-title       → title
      - .lf-owl-card-description → description
      - .lf-owl-card-id          → category
      - .lf-owl-card-difficulty span (last) → level text

    Args:
        card: BeautifulSoup element for one product card.

    Returns:
        Course dict or None if essential fields are missing.
    """
    title_el = card.select_one(".lf-owl-card-title")
    title = title_el.get_text(strip=True) if title_el else ""
    if not title:
        return None

    url = str(card.get("href", ""))
    if not url:
        return None
    if not url.startswith("http"):
        url = f"{BASE_URL}{url}"

    desc_el = card.select_one(".lf-owl-card-description")
    description = desc_el.get_text(strip=True) if desc_el else ""

    cat_el = card.select_one(".lf-owl-card-id")
    category = cat_el.get_text(strip=True) if cat_el else ""

    # Level lives inside .lf-owl-card-difficulty as the last <span>
    difficulty_el = card.select_one(".lf-owl-card-difficulty")
    if difficulty_el:
        spans = difficulty_el.select("span")
        level = spans[-1].get_text(strip=True) if spans else ""
    else:
        level = ""

    cert_available = "/certification/" in url

    return {
        "title": title,
        "description": description,
        "category": category,
        "level": level,
        "duration": "",  # not available on catalog cards; could enrich from detail page
        "url": url,
        "cert_available": cert_available,
    }


def scrape_catalog() -> list[dict]:
    """Scrape the LF training catalog and return list of course dicts.

    Returns:
        List of course dicts with title, description, category, level,
        duration, url, cert_available.

    Raises:
        ScraperError: On unrecoverable failures.
    """
    courses: list[dict] = []

    with _build_client() as client:
        if not _is_allowed(CATALOG_URL, client):
            raise ScraperError(f"robots.txt disallows scraping {CATALOG_URL}")

        logger.info("scraper_started", url=CATALOG_URL)

        try:
            soup = _fetch(CATALOG_URL, client)
        except Exception as exc:
            raise ScraperError(f"Failed to fetch catalog page: {exc}") from exc

        # Cards are <a class="lf-owl-card product-card ..."> elements
        cards = soup.select("a.product-card")
        logger.info("catalog_cards_found", count=len(cards))

        seen_urls: set[str] = set()
        for card in cards:
            course = _extract_course(card)
            if not course:
                continue

            url = course["url"]
            if url in seen_urls:
                continue
            seen_urls.add(url)

            courses.append(course)

            if len(courses) % 10 == 0:
                logger.info("scraper_progress", courses_scraped=len(courses))

    logger.info("scraper_complete", total_courses=len(courses))
    return courses


if __name__ == "__main__":
    configure_logging()
    log = structlog.get_logger(__name__)

    log.info("ingestion_scraper_started")
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        courses = scrape_catalog()
    except ScraperError as exc:
        log.error("scraper_failed", error=str(exc))
        raise SystemExit(1) from exc

    if not courses:
        log.error("no_courses_found")
        raise SystemExit(1)

    RAW_DATA_PATH.write_text(json.dumps(courses, indent=2, ensure_ascii=False))
    log.info("courses_saved", path=str(RAW_DATA_PATH), count=len(courses))
