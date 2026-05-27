import logging
import functools
from typing import Any, Callable

import structlog


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )


class LoggerMixin:
    @property
    def logger(self) -> structlog.BoundLogger:
        return structlog.get_logger(self.__class__.__name__)


def log_call(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = structlog.get_logger(func.__qualname__)
        logger.info("call_started", func=func.__name__)
        result = func(*args, **kwargs)
        logger.info("call_completed", func=func.__name__)
        return result

    return wrapper
