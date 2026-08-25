"""
provider.py

Defines the Pydantic model for provider metadata stored in the Apina registry.

Features:
    - Encodes provider identity, schema location, and documentation metadata.
    - Supports authentication, headers, and rate-limit configuration.

Dependencies: pydantic
"""

from typing import Any

from pydantic import BaseModel


class Provider(BaseModel):
    """Structured metadata for a single registered API provider."""

    id: str
    name: str
    version: str | None = None
    base_url: str
    schema_path: str
    documentation: str | None = None
    rate_limit: dict[str, Any] | None = None
    authentication: dict[str, Any] | None = None
    common_headers: dict[str, str] | None = None
    metadata: list[dict[str, Any]] | None = None
