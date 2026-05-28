MAX_RESULTS: int = 5
MIN_RESULTS: int = 1


class InvalidTopKError(ValueError):
    pass


def validate_top_k(k: int) -> int:
    """Validate that the requested number of results is within acceptable bounds.

    Args:
        k: Requested number of top results.

    Returns:
        The validated value of k.

    Raises:
        InvalidTopKError: If k is outside [MIN_RESULTS, MAX_RESULTS].
    """
    if k < MIN_RESULTS or k > MAX_RESULTS:
        raise InvalidTopKError(
            f"top_k must be between {MIN_RESULTS} and {MAX_RESULTS}, got {k}"
        )
    return k
