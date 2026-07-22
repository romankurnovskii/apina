"""
provider_registry.py

Maintains the in-memory registry of providers loaded from the configuration store.

Features:
    - Syncs provider configuration and schemas from GitHub when available.
    - Loads providers from the local configuration file as a fallback.
    - Exposes provider lookup helpers for the REST and MCP layers.

Dependencies: requests, pydantic
Side Effects: Reads and writes local provider configuration and schema files.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict
import requests
from models.provider import Provider
from core.config import settings

logger = logging.getLogger("apina.registry")


class ProviderRegistry:
    """Loads and serves provider metadata for the Apina service."""

    def __init__(self, config_dir: Path, schemas_dir: Path):
        """Initialize the registry and bootstrap provider data.

        Args:
            config_dir: Directory that contains providers.json.
            schemas_dir: Directory that stores OpenAPI schemas.
        """
        self.config_dir = config_dir
        self.schemas_dir = schemas_dir
        self.providers: Dict[str, Provider] = {}
        self.sync_from_github()
        self.load_providers()

    def sync_from_github(self):
        """Attempt to refresh provider definitions from the public GitHub repository."""
        github_repo = "romankurnovskii/apina"
        github_branch = "main"
        raw_url_base = (
            f"https://raw.githubusercontent.com/{github_repo}/{github_branch}"
        )
        providers_url = f"{raw_url_base}/config/providers.json"

        # Support GITHUB_TOKEN for private repositories
        github_token = os.environ.get("GITHUB_TOKEN")
        headers = {}
        if github_token:
            headers["Authorization"] = f"token {github_token}"

        logger.info(f"Syncing configuration from {providers_url}...")
        try:
            r = requests.get(providers_url, headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if "providers" in data:
                    self.config_dir.mkdir(parents=True, exist_ok=True)
                    providers_file = self.config_dir / "providers.json"
                    with open(providers_file, "w") as f:
                        json.dump(data, f, indent=2)
                    logger.info("Successfully synced providers.json from GitHub")

                    # Sync schema files for each provider
                    for p in data.get("providers", []):
                        schema_path = p.get("schema_path")
                        if schema_path:
                            schema_url = f"{raw_url_base}/schemas/{schema_path}"
                            logger.info(f"Syncing schema from {schema_url}...")
                            sr = requests.get(schema_url, headers=headers, timeout=5)
                            if sr.status_code == 200:
                                local_schema_file = self.schemas_dir / schema_path
                                local_schema_file.parent.mkdir(
                                    parents=True, exist_ok=True
                                )
                                with open(local_schema_file, "w") as sf:
                                    sf.write(sr.text)
                                logger.info(
                                    f"Successfully synced schema {schema_path} from GitHub"
                                )
                            else:
                                logger.warning(
                                    f"Failed to sync schema {schema_path} from GitHub: {sr.status_code}"
                                )
                else:
                    logger.warning(
                        "Invalid providers.json structure fetched from GitHub"
                    )
            else:
                logger.warning(
                    f"Failed to fetch providers.json from GitHub: {r.status_code}"
                )
        except Exception as e:
            logger.warning(
                f"Network error during GitHub sync, falling back to local files: {e}"
            )

    def load_providers(self):
        """Load provider definitions from the local providers.json file."""
        providers_file = self.config_dir / "providers.json"
        if not providers_file.exists():
            return
        with open(providers_file, "r") as f:
            data = json.load(f)
            for item in data.get("providers", []):
                provider = Provider(**item)
                self.providers[provider.id] = provider

    def get_all(self) -> List[Provider]:
        """Return every registered provider.

        Returns:
            list[Provider]: A list of provider models currently loaded in memory.
        """
        return list(self.providers.values())

    def get_by_id(self, provider_id: str) -> Optional[Provider]:
        """Return a provider by identifier if it exists.

        Args:
            provider_id: The provider identifier to look up.

        Returns:
            Provider | None: The matching provider, or None when absent.
        """
        return self.providers.get(provider_id)


provider_registry = ProviderRegistry(settings.config_dir, settings.schemas_dir)
