from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    app_name: str = "API-Aware"
    app_version: str = "0.1.0"
    schemas_dir: Path = Path("../schemas")
    config_dir: Path = Path("../config")
    cors_origins: list[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
