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
    def __init__(self, config_dir: Path, schemas_dir: Path):
        self.config_dir = config_dir
        self.schemas_dir = schemas_dir
        self.providers: Dict[str, Provider] = {}
        self.sync_from_github()
        self.load_providers()

    def sync_from_github(self):
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
        providers_file = self.config_dir / "providers.json"
        if not providers_file.exists():
            return
        with open(providers_file, "r") as f:
            data = json.load(f)
            for item in data.get("providers", []):
                provider = Provider(**item)
                self.providers[provider.id] = provider

    def get_all(self) -> List[Provider]:
        return list(self.providers.values())

    def get_by_id(self, provider_id: str) -> Optional[Provider]:
        return self.providers.get(provider_id)


provider_registry = ProviderRegistry(settings.config_dir, settings.schemas_dir)
