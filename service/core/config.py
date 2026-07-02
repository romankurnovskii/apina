from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_name: str = "API-Aware"
    app_version: str = "0.1.0"
    schemas_dir: Path = BASE_DIR / "schemas"
    config_dir: Path = BASE_DIR / "config"
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
