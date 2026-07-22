"""
endpoint.py

Defines the Pydantic models used to represent parsed OpenAPI endpoints.

Features:
    - Encodes endpoint parameters and request/response metadata.
    - Provides a normalized schema object for API response serialization.

Dependencies: pydantic
"""

from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class Parameter(BaseModel):
    """Structured metadata for a single OpenAPI parameter."""

    name: str
    type: str
    required: bool
    description: Optional[str] = None


class EndpointSchema(BaseModel):
    """Normalized representation of a single OpenAPI endpoint."""

    id: str
    path: str
    method: str
    full_url: str
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: Dict[str, List[Parameter]]
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Any]
    tags: Optional[List[str]] = None
