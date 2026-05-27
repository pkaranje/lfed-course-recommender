from typing import Any

MAX_RESULTS: int = 10


class RecommendationError(Exception):
    pass


def validate_recommendation(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate recommendation results before returning to caller.

    Args:
        results: List of course result dicts from retriever.

    Returns:
        Validated list, capped at MAX_RESULTS.

    Raises:
        RecommendationError: If results are malformed.
    """
    raise NotImplementedError
