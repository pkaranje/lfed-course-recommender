import re
from dataclasses import dataclass
from enum import StrEnum


class CourseCategory(StrEnum):
    cloud_containers = "cloud_containers"
    ai_ml = "ai_ml"
    devops = "devops"
    cybersecurity = "cybersecurity"
    linux = "linux"
    networking = "networking"
    blockchain = "blockchain"
    iot = "iot"
    web_dev = "web_dev"
    systems_engineering = "systems_engineering"
    open_source = "open_source"


class CourseLevel(StrEnum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


@dataclass
class CourseMetadata:
    title: str
    description: str
    category: CourseCategory
    level: CourseLevel
    url: str
    cert_available: bool


class InvalidCourseError(ValueError):
    pass


_REQUIRED_FIELDS = {
    "title",
    "description",
    "category",
    "level",
    "url",
    "cert_available",
}

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def validate_course_metadata(data: dict) -> CourseMetadata:
    """Parse and validate a raw course dict into a CourseMetadata.

    Args:
        data: Raw dict from scraper or ChromaDB metadata.

    Returns:
        Validated CourseMetadata.

    Raises:
        InvalidCourseError: If any required field is missing or invalid.
    """
    missing = _REQUIRED_FIELDS - data.keys()
    if missing:
        raise InvalidCourseError(
            f"Course metadata missing required fields: {sorted(missing)}"
        )

    title = str(data["title"]).strip()
    if not title:
        raise InvalidCourseError("Course 'title' must not be empty")

    description = str(data["description"]).strip()
    if not description:
        raise InvalidCourseError("Course 'description' must not be empty")

    try:
        category = CourseCategory(data["category"])
    except ValueError:
        valid = [e.value for e in CourseCategory]
        raise InvalidCourseError(
            f"Invalid course category '{data['category']}'. Must be one of: {valid}"
        )

    try:
        level = CourseLevel(data["level"])
    except ValueError:
        valid = [e.value for e in CourseLevel]
        raise InvalidCourseError(
            f"Invalid course level '{data['level']}'. Must be one of: {valid}"
        )

    url = str(data["url"]).strip()
    if not _URL_RE.match(url):
        raise InvalidCourseError(
            f"Course 'url' must start with http:// or https://: '{url}'"
        )

    cert_available = data["cert_available"]
    if not isinstance(cert_available, bool):
        raise InvalidCourseError(
            f"Course 'cert_available' must be a bool, got {type(cert_available).__name__}"
        )

    return CourseMetadata(
        title=title,
        description=description,
        category=category,
        level=level,
        url=url,
        cert_available=cert_available,
    )
