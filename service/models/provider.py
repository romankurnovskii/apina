"""
provider.py

Defines the Pydantic model for provider metadata stored in the Apina registry.

Features:
    - Encodes provider identity, schema location, and documentation metadata.
    - Supports authentication, headers, and rate-limit configuration.

Dependencies: pydantic
"""

from pydantic import BaseModel
from typing import Optional, Dict, List, Any


class Provider(BaseModel):
    """Structured metadata for a single registered API provider."""

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
