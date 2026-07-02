---
name: apina-api-registry
description: Discover, retrieve, and inspect OpenAPI schemas for registered API providers (like DEX Screener, Meteora DLMM, etc.). You MUST use this skill whenever you are asked to integrate, debug, or query any external REST API. Never guess API endpoint paths, base URLs, or query parameters; always query the Apina service first using MCP or REST to fetch the exact schema definition.
version: 1.1.0
---

# Apina API Registry Skill

Use this skill to interface with the Apina API registry. Apina serves as a centralized lookup engine containing OpenAPI schemas of registered Web3 and REST providers (such as DEX Screener, Meteora DLMM, etc.).

---

## 1. Agent Workflow: How to Use Apina (Core Instructions)

When you are asked to query or integrate an external API:

1. **Never Guess**: Do not make assumptions about the endpoint paths, parameter names, or base URLs of target services.
2. **Search the Registry**: Use the `apina` MCP tool `search_api` or query the REST endpoints to locate the target provider and endpoint.
3. **Construct the Request**: Use the retrieved schema (paths, query parameters, types) and the provider's `baseUrl` to construct the HTTP request.

### Example Walkthrough for Agents

If the user asks: _"Check the liquidity pools on Meteora matching the query 'SOL'"_:

#### Step A: Search for the endpoint

Call the MCP tool `search_api` (or query `GET /api/v1/providers/meteora/endpoints?search=pool`):

- **Tool Call**: `apina/search_api(query="pools", provider_id="meteora")`
- **Response Snippet**:
  ```
  Provider: Meteora DLMM API (meteora)
  Endpoint: GET /pools
  Summary: Pools
  Description: Returns a paginated list of pools
  Parameters:
    - query (string, optional): Search query matching pools by tokens/address
    - page_size (integer, optional): Max 1000
  ```

#### Step B: Fetch the Provider Base URL

Call the REST endpoint `GET /api/v1/providers/meteora` (or view `config/providers.json`):

- **Response**:
  ```json
  {
    "id": "meteora",
    "base_url": "https://dlmm.datapi.meteora.ag"
  }
  ```

#### Step C: Execute the Target Request

Now that you have the verified base URL and path parameters, construct and execute the call:

- **Request**: `GET https://dlmm.datapi.meteora.ag/pools?query=SOL&page_size=10`

---

## 2. API Reference for Agents

### A. MCP Server Interface

If the `apina` MCP server is registered in your client, use the following tool:

#### `search_api`

- **Arguments**:
  - `query` (string, required): A keyword to search endpoint paths, summaries, or descriptions (e.g. `"pools"`, `"pairs"`, `"token"`).
  - `provider_id` (string, optional): Filter search to a specific provider (e.g. `"meteora"`, `"dexscreener"`).
- **Returns**: Text block summarizing matching endpoints, including path, method, and query/path parameter requirements.

### B. REST API Interface

If the REST API is running (typically at `http://localhost:8081` or `http://localhost:8000`), you can query the endpoints directly via HTTP:

- **List Providers**: `GET /api/v1/providers`
  Returns all registered providers with metadata, base URLs, and total endpoint counts.
- **Get Provider Details**: `GET /api/v1/providers/{provider_id}`
  Returns the configuration (including `base_url`) for a specific provider.
- **List Endpoints**: `GET /api/v1/providers/{provider_id}/endpoints`
  Filter and list endpoints using query parameters: `search`, `method`, `tag`, `page`, and `limit`.
- **Get Endpoint Details**: `GET /api/v1/providers/{provider_id}/endpoints/{endpoint_id}`
  Returns the complete parameter schemas, responses, and description for a single endpoint.

---

## 3. Setup & Administration (For Humans)

To run the Apina service locally, you can choose between Docker Hub (recommended) or running python locally.

### Option A: Running via Docker Hub

The Docker image **`romankurnovskii/apina:latest`** bundles the registry and schemas internally.

- **Run the REST API Server**:

  ```bash
  docker run -d --name apina-api -p 8081:8000 romankurnovskii/apina:latest
  ```

  Verify via `http://localhost:8081/health`.

- **Configure the MCP Server (stdio transport)**:
  Add the following block to your client configuration (e.g. `mcp_config.json`):

  ```json
  {
    "mcpServers": {
      "apina": {
        "command": "docker",
        "args": ["run", "-i", "--rm", "romankurnovskii/apina:latest", "python", "service/mcp_server.py"]
      }
    }
  }
  ```

### Option B: Running Locally with Python

1. Install dependencies:
   ```bash
   pip install -r service/requirements.txt
   ```
2. Start the REST API:
   ```bash
   cd service
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. Register the local MCP Server:
   ```json
   {
     "mcpServers": {
       "apina": {
         "command": "python3",
         "args": ["/absolute/path/to/apina/service/mcp_server.py"]
       }
     }
   }
   ```
