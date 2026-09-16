import json
from pathlib import Path

from service.utils.openapi_parser import OpenAPIParser


def test_endpoint_without_responses(tmp_path: Path):
    # Minimal OpenAPI schema with one path and operation but no responses
    schema = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0"},
        "paths": {
            "/test": {
                "get": {
                    "operationId": "get_test",
                    "summary": "Test endpoint",
                    "responses": None,
                }
            }
        },
    }
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema))
    parser = OpenAPIParser(schema_file)
    eps = parser.get_endpoints("http://localhost")
    assert len(eps) == 1
    assert eps[0].responses == {}
