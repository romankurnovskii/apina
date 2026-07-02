# Apina 🐒🍌

Like a monkey that manages bananas, **Apina** manages your APIs.

Apina provides a centralized REST API and a Model Context Protocol (MCP) server so that any AI agent can quickly discover and understand the schemas and references of any API registered in this project.

## Philosophy

The goal is simple: instead of teaching every agent about every new endpoint, you register the APIs here. Apina exposes them in a unified way.

- **REST API**: Programmatically get a list of registered endpoints, their paths, and schemas.
- **MCP Server**: Provide your AI agents with a dynamic tool to search for APIs. An agent can ask, "Is there an endpoint on DEX Screener?" or "How do I check a Solana balance?", and the MCP server will guide it to the correct schema.

## Quick Start

### 1-Minute Service Start

```bash
# Start the REST API service
docker-compose up --build

# Test it
curl http://localhost:8000/health
```

**Done!** The REST API is running at http://localhost:8000.

### Running the MCP Server

You can run the built-in MCP server locally to allow your AI agents to query the APIs:

```bash
# Install dependencies
pip install -r service/requirements.txt

# Run the MCP server
python service/mcp_server.py
```

You can then connect your compatible AI agent (like Claude Desktop or any MCP client) to use `search_api` tools.

## Adding a Provider

Add your provider configuration in `config/providers.json` and place its OpenAPI schema in the `schemas/` directory. Apina will automatically parse it and expose it via both the REST API and the MCP Server.
