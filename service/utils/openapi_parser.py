"""
openapi_parser.py

Parses local OpenAPI schemas into normalized endpoint structures for Apina.

Features:
    - Loads a JSON schema from disk and resolves local $ref definitions.
    - Converts OpenAPI operations into EndpointSchema models for the API layer.
    - Extracts parameters, request bodies, responses, and tags.

Dependencies: json, pathlib
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from models.endpoint import EndpointSchema, Parameter


class OpenAPIParser:
    """Parses OpenAPI JSON schemas into typed endpoint metadata."""

    def __init__(self, schema_path: Path):
        """Initialize the parser for a specific schema file.

        Args:
            schema_path: Path to the OpenAPI schema JSON file.
        """
        self.schema_path = schema_path
        self.schema: Dict[str, Any] = {}
        self.load_schema()

    def load_schema(self):
        """Load the schema JSON from disk when the file exists."""
        if not self.schema_path.exists():
            return
        with open(self.schema_path, "r") as f:
            self.schema = json.load(f)

    def _resolve_refs(self, node: Any, seen: Optional[set] = None) -> Any:
        """Resolve local OpenAPI $ref values recursively.

        Args:
            node: The schema node to resolve.
            seen: A set of already-traversed references to prevent recursion loops.

        Returns:
            Any: The resolved structure with local references expanded.
        """
        if seen is None:
            seen = set()

        if isinstance(node, dict):
            if "$ref" in node:
                ref_path = node["$ref"]
                if ref_path in seen:
                    return {
                        "type": "object",
                        "description": f"Circular reference to {ref_path}",
                    }

                # Copy seen set to track paths down this specific traversal branch
                new_seen = seen.copy()
                new_seen.add(ref_path)

                resolved = self._resolve_ref_path(ref_path)
                return self._resolve_refs(resolved, new_seen)
            else:
                return {k: self._resolve_refs(v, seen) for k, v in node.items()}
        elif isinstance(node, list):
            return [self._resolve_refs(item, seen) for item in node]
        return node

    def _resolve_ref_path(self, ref_path: str) -> Any:
        """Resolve a local OpenAPI reference path against the loaded schema."""
        if not ref_path.startswith("#/"):
            return {
                "type": "object",
                "description": f"External reference {ref_path} not supported",
            }

        parts = ref_path.lstrip("#/").split("/")
        current = self.schema
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return {
                    "type": "object",
                    "description": f"Failed to resolve ref path: {ref_path}",
                }
        return current

    def get_endpoints(self, base_url: str) -> List[EndpointSchema]:
        """Convert the parsed schema into endpoint models.

        Args:
            base_url: The base URL that should prefix the endpoint paths.

        Returns:
            list[EndpointSchema]: A list of normalized endpoint definitions.
        """
        endpoints = []
        paths = self.schema.get("paths", {})
        for path, path_item in paths.items():
            for method, method_item in path_item.items():
                if method.lower() not in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "options",
                    "head",
                ]:
                    continue

                # Generate unique endpoint ID
                op_id = method_item.get("operationId")
                if not op_id:
                    clean_path = (
                        path.strip("/")
                        .replace("/", "-")
                        .replace("{", "")
                        .replace("}", "")
                    )
                    op_id = f"{method.lower()}-{clean_path}"

                summary = method_item.get("summary")
                description = method_item.get("description")
                tags = method_item.get("tags")

                # Resolve references inside the parameters and responses
                resolved_method_item = self._resolve_refs(method_item)
                resolved_path_item = self._resolve_refs(path_item)

                # Parse parameters
                parameters_data = {"path": [], "query": [], "header": [], "cookie": []}
                # Retrieve parameters defined in method or path level
                raw_params = resolved_method_item.get(
                    "parameters", []
                ) + resolved_path_item.get("parameters", [])
                for param in raw_params:
                    param_in = param.get("in", "query")
                    name = param.get("name")
                    required = param.get("required", False)
                    desc = param.get("description")
                    schema_type = "string"
                    if "schema" in param:
                        raw_type = param["schema"].get("type", "string")
                        if isinstance(raw_type, list):
                            non_null = [t for t in raw_type if t != "null"]
                            schema_type = non_null[0] if non_null else "string"
                        else:
                            schema_type = raw_type

                    parameter = Parameter(
                        name=name, type=schema_type, required=required, description=desc
                    )
                    if param_in in parameters_data:
                        parameters_data[param_in].append(parameter)

                responses = resolved_method_item.get("responses", {})

                # Parse request body schema if present
                request_body_schema = None
                request_body_data = resolved_method_item.get("requestBody")
                if request_body_data and isinstance(request_body_data, dict):
                    content = request_body_data.get("content", {})
                    # Try to extract JSON schema, otherwise fallback to first schema found
                    json_content = content.get("application/json", {})
                    if "schema" in json_content:
                        request_body_schema = json_content["schema"]
                    elif content:
                        first_content = next(iter(content.values()), {})
                        request_body_schema = first_content.get("schema")

                endpoint = EndpointSchema(
                    id=op_id,
                    path=path,
                    method=method.upper(),
                    full_url=f"{base_url.rstrip('/')}/{path.lstrip('/')}",
                    summary=summary,
                    description=description,
                    parameters=parameters_data,
                    request_body=request_body_schema,
                    responses=responses,
                    tags=tags,
                )
                endpoints.append(endpoint)
        return endpoints
