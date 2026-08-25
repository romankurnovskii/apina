"""
endpoint.py

Defines the Pydantic models used to represent parsed OpenAPI endpoints.

Features:
    - Encodes endpoint parameters and request/response metadata.
    - Provides a normalized schema object for API response serialization.

Dependencies: pydantic
"""

from typing import Any

from pydantic import BaseModel


class Parameter(BaseModel):
    """Structured metadata for a single OpenAPI parameter."""

    description: str | None = None
    required: bool
    name: str
    type: str


class EndpointSchema(BaseModel):
    """Normalized representation of a single OpenAPI endpoint."""

    id: str
    path: str
    method: str
    full_url: str
    summary: str | None = None
    description: str | None = None
    parameters: dict[str, list["Parameter"]]
    request_body: dict[str, Any] | None = None
    responses: dict[str, Any]
    tags: list[str] | None = None
