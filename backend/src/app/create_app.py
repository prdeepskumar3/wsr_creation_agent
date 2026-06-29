from api.v1.router import api_v1_router
from fastapi import FastAPI

from app.settings import AppSettings


def create_app(settings: AppSettings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    resolved_settings = settings or AppSettings()
    app = FastAPI(title=resolved_settings.app_name, version=resolved_settings.app_version)
    app.include_router(api_v1_router, prefix="/api/v1")
    return app
