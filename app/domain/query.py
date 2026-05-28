import re
import unicodedata

MAX_QUERY_LENGTH: int = 500  # default, overridable via parameter

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WHITESPACE_RE = re.compile(r"\s+")


class QueryTooLongError(ValueError):
    pass


class QueryEmptyError(ValueError):
    pass


def sanitise_input(text: str) -> str:
    """Strip control characters, collapse whitespace, and trim the string.

    Args:
        text: Raw user-supplied string.

    Returns:
        Sanitised string safe to pass downstream.
    """
    text = unicodedata.normalize("NFC", text)
    text = _CONTROL_CHAR_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def validate_user_query(query: str, max_length: int = MAX_QUERY_LENGTH) -> str:
    """Sanitise and validate a user query string.

    Args:
        query: Raw query string from the API request.
        max_length: Maximum allowed length after sanitisation.

    Returns:
        Cleaned, length-checked query ready for embedding.

    Raises:
        QueryEmptyError: If the query is empty after sanitisation.
        QueryTooLongError: If the query exceeds max_length characters.
    """
    clean = sanitise_input(query)
    if not clean:
        raise QueryEmptyError("Query must not be empty")
    if len(clean) > max_length:
        raise QueryTooLongError(
            f"Query length {len(clean)} exceeds maximum of {max_length} characters"
        )
    return clean
