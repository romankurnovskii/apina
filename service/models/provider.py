from pydantic import BaseModel
from typing import Optional, Dict, List, Any

class Provider(BaseModel):
    id: str
    name: str
    version: Optional[str] = None
    base_url: str
    schema_path: str
    documentation: Optional[str] = None
    rate_limit: Optional[Dict[str, Any]] = None
    authentication: Optional[Dict[str, Any]] = None
    common_headers: Optional[Dict[str, str]] = None
    metadata: Optional[List[Dict[str, Any]]] = None
