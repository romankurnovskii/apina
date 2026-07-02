import asyncio
import sys
import os

# Add parent dir to path so we can import core and utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional

from core.provider_registry import provider_registry
from core.config import settings
from utils.openapi_parser import OpenAPIParser

# Initialize FastMCP server
mcp = FastMCP("apina-server", description="Apina MCP Server - find API schemas and endpoints")

@mcp.tool()
def search_api(query: str, provider_id: Optional[str] = None) -> str:
    """
    Search for API endpoints across registered providers.
    
    Args:
        query: Search term for endpoint paths, summaries, or descriptions (e.g., 'solana balance', 'dexscreener').
        provider_id: Optional specific provider to search within.
    """
    results = []
    
    providers = provider_registry.get_all()
    if provider_id:
        providers = [p for p in providers if p.id == provider_id]
        
    query_lower = query.lower()
    
    for p in providers:
        schema_path = settings.schemas_dir / p.schema_path
        try:
            parser = OpenAPIParser(schema_path)
            endpoints = parser.get_endpoints(p.base_url)
        except Exception as e:
            continue
            
        for ep in endpoints:
            in_path = query_lower in ep.path.lower()
            in_summary = query_lower in (ep.summary or "").lower()
            in_desc = query_lower in (ep.description or "").lower()
            in_tags = any(query_lower in (t or "").lower() for t in (ep.tags or []))
            in_provider = query_lower in p.name.lower() or query_lower in p.id.lower()
            
            if in_path or in_summary or in_desc or in_tags or in_provider:
                results.append(
                    f"Provider: {p.name} ({p.id})\n"
                    f"Endpoint: {ep.method} {ep.path}\n"
                    f"Summary: {ep.summary}\n"
                    f"Description: {ep.description}\n"
                    "---"
                )
                
    if not results:
        return f"No endpoints found matching query: {query}"
        
    return "\n".join(results)

if __name__ == "__main__":
    # Run the stdio server
    mcp.run(transport='stdio')
