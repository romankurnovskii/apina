---
name: apina-js-sdk
description: Unified dynamic JavaScript SDK client to interact with the Apina API registry and execute third-party API calls (Meteora, DexScreener, DefiLlama).
---

# Apina JS SDK Agent playbook

Use this skill when you need to make API calls to third-party endpoints registered on the Apina server (e.g. DexScreener, Meteora DLMM, DefiLlama) using JavaScript/TypeScript.

## Installation & Setup

1. **Import the client**:
   ```javascript
   import { ApinaClient } from 'apina-sdk';
   ```

2. **Initialize with the Apina server registry URL**:
   ```javascript
   const apina = new ApinaClient({ registryUrl: "http://localhost:8000" });
   await apina.init(); // Fetches and loads registry metadata
   ```

---

## Executing Dynamic API Calls

The SDK uses ES6 `Proxy` to intercept arbitrary method calls. You can invoke any endpoint on any provider by namespacing the call:

```javascript
const response = await apina.<providerId>.<endpointId>(args);
```

### 1. Naming & Case Conventions

The client automatically maps camelCase or snake_case methods to the underlying registry endpoint IDs (which are typically kebab-case).

- **Registry ID**: `get-token-profiles-latest-v1` $\rightarrow$ Call as: `apina.dexscreener.getTokenProfilesLatestV1()`
- **Registry ID**: `get-metas-meta-v1-slug` $\rightarrow$ Call as: `apina.dexscreener.getMetasMetaV1Slug({ slug: "solana" })`
- **Registry ID**: `Get Pools` (Meteora) $\rightarrow$ Call as: `apina.meteora.getPools({ page_size: 2 })`

> [!NOTE]
> The Apina server performs **case-insensitive matching** and strips hyphens, underscores, and spaces to match. For example, `getPools`, `get_pools`, or `get-pools` will all resolve to Meteora's `"Get Pools"` endpoint.

### 2. Passing Arguments (Flat vs Structured)

The SDK supports both flat arguments (recommended for simple query/path parameters) and structured args (when custom headers or body payloads are required).

#### Flat Arguments (Query / Path)
Pass a flat object. The proxy server maps fields to their correct locations:
```javascript
const pools = await apina.meteora.getPools({ page_size: 5 });
```

#### Structured Arguments (Body / Headers)
To pass a POST body or custom headers, use the structured schema:
```javascript
const response = await apina.provider.endpoint({
  parameters: {
     pathOrQueryParam: "value"
  },
  body: {
     jsonPayloadKey: "value"
  },
  headers: {
     "Custom-Header": "value"
  }
});
```
