"""
provider_registry.py

Maintains the in-memory registry of providers loaded from GitHub (single source of truth).

Features:
    - Fetches provider configuration and schemas from GitHub on startup.
    - Caches fetched data locally for performance.
    - Exposes provider lookup helpers for the REST and MCP layers.

Dependencies: requests, pydantic
Side Effects: Reads and writes local provider configuration and schema files (cache only).
"""

import json
import logging
import os
from pathlib import Path

import requests
from core.config import settings
from models.provider import Provider

logger = logging.getLogger("apina.registry")

GITHUB_REPO = "romankurnovskii/apina"
GITHUB_BRANCH = "main"
RAW_URL_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"


class ProviderRegistry:
    """Loads and serves provider metadata from GitHub (canonical source)."""

    def __init__(self, config_dir: Path, schemas_dir: Path):
        """Initialize the registry and bootstrap provider data from GitHub.

        Args:
            config_dir: Directory to cache providers.json.
            schemas_dir: Directory to cache OpenAPI schemas.
        """
        self.config_dir = config_dir
        self.schemas_dir = schemas_dir
        self.providers: dict[str, Provider] = {}
        self.load_from_github()

    def load_from_github(self):
        """Fetch provider definitions from GitHub (single source of truth).

        Raises:
            RuntimeError: If GitHub cannot be reached or returns invalid data.
        """
        providers_url = f"{RAW_URL_BASE}/config/providers.json"

        # Support GITHUB_TOKEN for private repositories or rate limit increases
        github_token = os.environ.get("GITHUB_TOKEN")
        headers = {"Authorization": f"token {github_token}"} if github_token else {}

        logger.info(f"Loading providers from GitHub: {providers_url}")
        try:
            r = requests.get(providers_url, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()

            if "providers" not in data:
                raise ValueError(
                    "Invalid providers.json structure: missing 'providers' key"
                )

            # Cache providers.json locally
            self.config_dir.mkdir(parents=True, exist_ok=True)
            providers_file = self.config_dir / "providers.json"
            with open(providers_file, "w") as f:
                json.dump(data, f, indent=2)
            logger.info("Cached providers.json locally")

            # Fetch and cache schema files for each provider
            for p in data.get("providers", []):
                schema_path = p.get("schema_path")
                if schema_path:
                    schema_url = f"{RAW_URL_BASE}/schemas/{schema_path}"
                    try:
                        sr = requests.get(schema_url, headers=headers, timeout=10)
                        sr.raise_for_status()

                        local_schema_file = self.schemas_dir / schema_path
                        local_schema_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(local_schema_file, "w") as sf:
                            sf.write(sr.text)
                        logger.info(f"Cached schema: {schema_path}")
                    except requests.RequestException as e:
                        logger.warning(
                            f"Failed to fetch schema {schema_path} from GitHub: {e}"
                        )

            # Load into memory
            self.load_providers()
            logger.info(
                f"Successfully loaded {len(self.providers)} providers from GitHub"
            )

        except requests.RequestException as e:
            logger.critical(f"Failed to fetch providers from GitHub: {e}")
            raise RuntimeError(
                "Cannot start service: GitHub configuration unavailable"
            ) from e
        except (json.JSONDecodeError, ValueError) as e:
            logger.critical(f"Invalid configuration from GitHub: {e}")
            raise RuntimeError(
                "Cannot start service: Invalid GitHub configuration"
            ) from e

    def load_providers(self):
        """Load provider definitions from the cached local providers.json file."""
        providers_file = self.config_dir / "providers.json"
        if not providers_file.exists():
            logger.warning("No cached providers.json found")
            return
        with open(providers_file, "r") as f:
            data = json.load(f)
            for item in data.get("providers", []):
                provider = Provider(**item)
                self.providers[provider.id] = provider

    def get_all(self) -> list[Provider]:
        """Return every registered provider.

        Returns:
            list[Provider]: A list of provider models currently loaded in memory.
        """
        return list(self.providers.values())

    def get_by_id(self, provider_id: str) -> Provider | None:
        """Return a provider by identifier if it exists.

        Args:
            provider_id: The provider identifier to look up.

        Returns:
            Provider | None: The matching provider, or None when absent.
        """
        return self.providers.get(provider_id)


# Bootstrap the registry on module load
provider_registry = ProviderRegistry(settings.config_dir, settings.schemas_dir)
