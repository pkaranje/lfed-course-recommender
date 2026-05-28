import logging
import os
import time
import functools
from typing import Any, Callable

import structlog


def configure_logging() -> None:
    is_prod = os.getenv("ENV", "dev").lower() == "prod"

    renderer: Any = (
        structlog.processors.JSONRenderer()
        if is_prod
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )


class LoggerMixin:
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        return structlog.get_logger(self.__class__.__name__)


def log_call(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = structlog.get_logger(func.__qualname__)
        logger.info("call_started", func=func.__name__)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info("call_completed", func=func.__name__, duration_ms=duration_ms)
        return result

    return wrapper
