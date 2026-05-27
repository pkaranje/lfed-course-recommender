from app.core.config import settings


class QueryTooLongError(Exception):
    pass


def sanitise_input(text: str) -> str:
    """Strip dangerous characters from user input before LLM call.

    Args:
        text: Raw user-supplied string.

    Returns:
        Sanitised string safe to pass to LLM.
    """
    raise NotImplementedError


def validate_user_query(query: str) -> str:
    """Validate and sanitise user query.

    Args:
        query: Raw query string.

    Returns:
        Cleaned, length-checked query.

    Raises:
        QueryTooLongError: If query exceeds MAX_QUERY_LENGTH.
    """
    raise NotImplementedError
