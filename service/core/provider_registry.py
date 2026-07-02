import json
from pathlib import Path
from typing import List, Optional, Dict
from models.provider import Provider
from core.config import settings

class ProviderRegistry:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.providers: Dict[str, Provider] = {}
        self.load_providers()

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

provider_registry = ProviderRegistry(settings.config_dir)
