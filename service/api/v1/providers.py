"""
providers.py

Provides the REST API routes for listing providers and invoking their endpoints.

Features:
    - Lists provider metadata and endpoint counts from the registry.
    - Returns endpoint definitions and proxy execution results for a provider.
    - Supports filtering, pagination, and payload-based endpoint calls.

Dependencies: fastapi, requests
Side Effects: Performs outbound HTTP requests when calling registered endpoints.
"""

from fastapi import APIRouter, HTTPException, Body, Response
from typing import Optional, Dict, Any
import requests
from core.provider_registry import provider_registry
from core.config import settings
from utils.openapi_parser import OpenAPIParser
from models.endpoint import EndpointSchema

router = APIRouter()


@router.get("", response_model=Dict[str, Any])
def list_providers():
    """List all registered providers and their endpoint counts.

    Returns:
        dict: A payload containing a provider list and total count.
    """
    providers = provider_registry.get_all()
    result = []
    for p in providers:
        schema_path = settings.schemas_dir / p.schema_path
        parser = OpenAPIParser(schema_path)
        endpoints = parser.get_endpoints(p.base_url)

        result.append(
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "baseUrl": p.base_url,
                "authType": p.authentication.get("type")
                if p.authentication
                else "none",
                "endpointCount": len(endpoints),
                "documentation": p.documentation,
            }
        )
    return {"providers": result, "total": len(result)}


@router.get("/{provider_id}")
def get_provider(provider_id: str):
    """Return a single provider by identifier.

    Args:
        provider_id: The provider identifier to load.

    Returns:
        Provider: The matching provider model.

    Raises:
        HTTPException: If the provider does not exist.
    """
    p = provider_registry.get_by_id(provider_id)
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")
    return p


@router.get("/{provider_id}/endpoints", response_model=Dict[str, Any])
def list_endpoints(
    provider_id: str,
    tag: Optional[str] = None,
    method: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 100,
):
    """List endpoints for a provider with optional filtering and pagination.

    Args:
        provider_id: The provider identifier to query.
        tag: Optional tag filter for matching endpoints.
        method: Optional HTTP method filter.
        search: Optional keyword search across endpoint metadata.
        page: Page number for pagination.
        limit: Number of items to return per page.

    Returns:
        dict: A payload containing the matching endpoints and pagination metadata.

    Raises:
        HTTPException: If the provider does not exist.
    """
    p = provider_registry.get_by_id(provider_id)
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")

    schema_path = settings.schemas_dir / p.schema_path
    parser = OpenAPIParser(schema_path)
    endpoints = parser.get_endpoints(p.base_url)

    filtered_endpoints = []
    for ep in endpoints:
        if method and ep.method.upper() != method.upper():
            continue
        if tag and tag.lower() not in [t.lower() for t in (ep.tags or [])]:
            continue
        if search:
            search_lower = search.lower()
            in_path = search_lower in ep.path.lower()
            in_summary = search_lower in (ep.summary or "").lower()
            in_description = search_lower in (ep.description or "").lower()
            if not (in_path or in_summary or in_description):
                continue
        filtered_endpoints.append(ep)

    # Paginate results
    start = (page - 1) * limit
    end = start + limit
    paginated_endpoints = filtered_endpoints[start:end]

    return {
        "endpoints": paginated_endpoints,
        "total": len(filtered_endpoints),
        "page": page,
        "limit": limit,
    }


@router.get("/{provider_id}/endpoints/{endpoint_id}", response_model=EndpointSchema)
def get_endpoint(provider_id: str, endpoint_id: str):
    """Return a single endpoint schema by provider and endpoint identifier.

    Args:
        provider_id: The provider identifier that owns the endpoint.
        endpoint_id: The endpoint identifier to resolve.

    Returns:
        EndpointSchema: The matching endpoint definition.

    Raises:
        HTTPException: If the provider or endpoint does not exist.
    """
    p = provider_registry.get_by_id(provider_id)
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")

    schema_path = settings.schemas_dir / p.schema_path
    parser = OpenAPIParser(schema_path)
    endpoints = parser.get_endpoints(p.base_url)

    normalized_endpoint_id = (
        endpoint_id.lower().replace("-", "").replace("_", "").replace(" ", "")
    )
    for ep in endpoints:
        normalized_target_id = (
            ep.id.lower().replace("-", "").replace("_", "").replace(" ", "")
        )
        if normalized_target_id == normalized_endpoint_id:
            return ep

    raise HTTPException(status_code=404, detail="Endpoint not found")


@router.post("/{provider_id}/endpoints/{endpoint_id}/call")
def call_endpoint(
    provider_id: str,
    endpoint_id: str,
    payload: Dict[str, Any] = Body(
        default={"parameters": {}, "body": {}, "headers": {}}
    ),
):
    """Proxy an endpoint call to the upstream provider.

    Args:
        provider_id: The provider identifier that owns the endpoint.
        endpoint_id: The endpoint identifier to call.
        payload: Structured parameters, body, and headers for the request.

    Returns:
        Response: The downstream response payload and status code.

    Raises:
        HTTPException: If the provider or endpoint is missing, or proxying fails.
    """
    p = provider_registry.get_by_id(provider_id)
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")

    schema_path = settings.schemas_dir / p.schema_path
    parser = OpenAPIParser(schema_path)
    endpoints = parser.get_endpoints(p.base_url)

    target_ep = None
    normalized_endpoint_id = (
        endpoint_id.lower().replace("-", "").replace("_", "").replace(" ", "")
    )
    for ep in endpoints:
        normalized_target_id = (
            ep.id.lower().replace("-", "").replace("_", "").replace(" ", "")
        )
        if normalized_target_id == normalized_endpoint_id:
            target_ep = ep
            break

    if not target_ep:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    # Construct request inputs
    user_params = payload.get("parameters") or {}
    user_body = payload.get("body")
    user_headers = payload.get("headers") or {}

    # Map parameters to their correct target locations
    path_params = {}
    query_params = {}
    header_params = {}
    cookie_params = {}

    # Separate parameters according to the OpenAPI schema
    for param_type, params_list in target_ep.parameters.items():
        for param in params_list:
            param_name = param.name
            if param_name in user_params:
                val = user_params[param_name]
                if param_type == "path":
                    path_params[param_name] = str(val)
                elif param_type == "query":
                    query_params[param_name] = val
                elif param_type == "header":
                    header_params[param_name] = str(val)
                elif param_type == "cookie":
                    cookie_params[param_name] = val
            elif param.required and param_type == "path":
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required path parameter: {param_name}",
                )

    # Build the dynamic URL
    resolved_path = target_ep.path
    for name, val in path_params.items():
        resolved_path = resolved_path.replace(f"{{{name}}}", val)

    full_url = f"{p.base_url.rstrip('/')}/{resolved_path.lstrip('/')}"

    # Merge headers
    headers = {}
    if p.common_headers:
        headers.update(p.common_headers)
    headers.update(header_params)
    headers.update(user_headers)

    # Perform the HTTP call
    try:
        method = target_ep.method.upper()
        req_kwargs = {
            "method": method,
            "url": full_url,
            "params": query_params,
            "headers": headers,
            "cookies": cookie_params,
            "timeout": 30,
        }
        if method in ["POST", "PUT", "PATCH"] and user_body is not None:
            req_kwargs["json"] = user_body

        resp = requests.request(**req_kwargs)

        return Response(
            content=resp.text,
            status_code=resp.status_code,
            media_type=resp.headers.get("Content-Type", "application/json"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to proxy request: {str(e)}"
        )
