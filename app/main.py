"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import router as api_v1_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")

    # Initialize database connection pool, etc.
    # TODO: Add database initialization

    yield

    # Shutdown
    print("Shutting down application")
    # TODO: Add cleanup tasks


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_v1_router, prefix=settings.api_prefix)

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> JSONResponse:
        """Root endpoint with API information."""
        return JSONResponse(
            content={
                "name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment,
                "docs": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json",
            }
        )

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> JSONResponse:
        """Basic health check endpoint."""
        return JSONResponse(
            content={
                "status": "healthy",
                "version": settings.app_version,
                "environment": settings.environment,
            }
        )

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
