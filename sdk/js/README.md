# Apina Client SDK

The unified, dynamic JavaScript/TypeScript client library for the **Apina** API registry. 

## Features

- **Unified Client**: Interact with all registered API providers (DexScreener, Meteora, DefiLlama, etc.) from a single client instance.
- **Dynamic Method Invocation**: Uses ES6 `Proxy` under the hood. No need to update the client library when new providers are registered on the Apina server.
- **Robust Parameter Mapping**: The registry proxy automatically maps and formats path parameters, query parameters, cookies, and payloads to match the provider's OpenAPI spec.
- **Zero Runtime Dependencies**: Extremely lightweight. Built on top of native `fetch` (requires Node.js 18+ or standard browser environments).

---

## Installation

Install via npm (or link locally during development):

```bash
npm install apina-sdk
```

---

## Usage

### 1. Initialization

Point the client to your running Apina registry server:

```typescript
import { ApinaClient } from 'apina-sdk';

const apina = new ApinaClient({ registryUrl: "http://localhost:8000" });
await apina.init(); // Fetches registered providers
```

### 2. Dynamic Method Calls

Call endpoints using the dynamic namespace syntax:

```typescript
// 1. Fetch token profiles from DexScreener (GET endpoint)
const tokenData = await apina.dexscreener.getTokenProfiles({
  tokenAddress: "0x..."
});

// 2. Fetch Meteora DLMM pool information
const pools = await apina.meteora.getDlmmPools({ limit: 10 });
```

### 3. Explicit / Custom Calls

For full control, or if you prefer an explicit calling signature:

```typescript
const data = await apina.call("dexscreener", "get-token-profiles", {
  parameters: {
    tokenAddress: "0x..."
  },
  headers: {
    "Custom-Header": "value"
  }
});
```
