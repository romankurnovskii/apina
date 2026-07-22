"""
main.py

Apina REST API entry point - serves provider metadata and proxied endpoint calls.

Entry Point: Yes
Service: Apina REST API
Port: 8000

Features:
    - Exposes health and status endpoints for the REST service.
    - Mounts the providers router under the v1 API namespace.
    - Configures CORS for browser-based clients.

Dependencies: fastapi
Side Effects: Starts the FastAPI application and serves HTTP requests.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.v1.providers import router as providers_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(providers_router, prefix="/api/v1/providers", tags=["Providers"])


@app.get("/health")
def health_check():
    """Return a simple health payload for liveness checks.

    Returns:
        dict: A JSON payload with the service status and API version.
    """
    return {"status": "healthy", "version": settings.app_version}


@app.get("/")
def root():
    """Return a welcome message for the API root endpoint.

    Returns:
        dict: A greeting payload for the Apina API service.
    """
    return {"message": f"Welcome to {settings.app_name} API"}
