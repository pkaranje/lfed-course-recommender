from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, recommend, search
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="LF Course Recommender",
        description="AI-powered course recommendation for the Linux Foundation catalog",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8501", "http://frontend:8501"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    application.include_router(health.router, prefix="/api/v1")
    application.include_router(recommend.router, prefix="/api/v1")
    application.include_router(search.router, prefix="/api/v1")

    return application


app = create_app()
