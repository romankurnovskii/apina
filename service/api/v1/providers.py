from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from core.provider_registry import provider_registry
from core.config import settings
from utils.openapi_parser import OpenAPIParser
from models.endpoint import EndpointSchema

router = APIRouter()


@router.get("", response_model=Dict[str, Any])
def list_providers():
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
    p = provider_registry.get_by_id(provider_id)
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")

    schema_path = settings.schemas_dir / p.schema_path
    parser = OpenAPIParser(schema_path)
    endpoints = parser.get_endpoints(p.base_url)

    for ep in endpoints:
        if ep.id == endpoint_id:
            return ep

    raise HTTPException(status_code=404, detail="Endpoint not found")
