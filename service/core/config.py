"""
config.py

Loads application settings for the Apina REST and MCP services.

Features:
    - Defines the shared settings object for the service.
    - Resolves paths to configuration and schema directories.
    - Supports environment-based overrides via pydantic settings.

Dependencies: pydantic_settings
Side Effects: Reads environment variables from the local .env file.
"""

from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application configuration container for the Apina service."""

    app_name: str = "API-Aware"
    app_version: str = "0.1.0"
    schemas_dir: Path = BASE_DIR / "schemas"
    config_dir: Path = BASE_DIR / "config"
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
