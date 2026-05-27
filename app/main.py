from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware
from app.api.routes import health, recommend, search


def create_app() -> FastAPI:
    configure_logging()

    application = FastAPI(
        title="LF Course Recommender",
        description="AI-powered course recommendation for the Linux Foundation catalog",
        version="0.1.0",
    )

    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8501"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    application.include_router(health.router)
    application.include_router(recommend.router)
    application.include_router(search.router)

    return application


app = create_app()
