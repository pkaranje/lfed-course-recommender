from enum import Enum
from typing import Any


class CourseCategoryError(Exception):
    pass


class CourseCategory(str, Enum):
    CLOUD = "Cloud & Containers"
    LINUX = "Linux Kernel & Systems"
    NETWORKING = "Networking"
    SECURITY = "Security"
    DEVOPS = "DevOps & Site Reliability"
    KUBERNETES = "Kubernetes"
    DEVSECOPS = "DevSecOps"
    OTHER = "Other"


def validate_course_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Validate course metadata fields.

    Args:
        metadata: Raw metadata dict from ChromaDB or scraper.

    Returns:
        Validated metadata dict.

    Raises:
        CourseCategoryError: If category is invalid.
    """
    raise NotImplementedError
