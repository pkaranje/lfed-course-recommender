import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)

        logger.info("request_started", method=request.method, path=request.url.path)
        response = await call_next(request)
        logger.info("request_completed", status_code=response.status_code)

        structlog.contextvars.clear_contextvars()
        return response
