/**
 * @file index.ts
 * @description Provides the JavaScript SDK client for calling Apina registry endpoints.
 *
 * @features
 * - Exposes a dynamic proxy client for provider and endpoint access
 * - Initializes provider metadata from the registry API
 * - Proxies endpoint calls to the registry gateway
 *
 * @dependencies fetch
 * @sideEffects Performs HTTP calls to the Apina registry API
 */
interface ProviderSummary {
  id: string;
  name: string;
  version?: string;
  baseUrl: string;
  authType?: string;
  endpointCount: number;
  documentation?: string;
}

interface CallArgs {
  parameters?: Record<string, unknown>;
  body?: unknown;
  headers?: Record<string, string>;
}

interface ProviderListResponse {
  providers: ProviderSummary[];
}

export class ApinaClient {
  private registryUrl: string;
  private providers: Record<string, ProviderSummary> = {};

  /**
   * Creates a new Apina client bound to a registry base URL.
   *
   * @param {{ registryUrl: string }} config - Registry URL configuration.
   */
  constructor(config: { registryUrl: string }) {
    this.registryUrl = config.registryUrl.replace(/\/$/, '');

    // Return a Proxy to intercept calls like: client.providerId.endpointId(args)
    return new Proxy(this, {
      get(target: ApinaClient, prop: string | symbol) {
        if (prop in target || typeof prop === 'symbol') {
          return target[prop as keyof ApinaClient];
        }

        const providerId = String(prop);

        return new Proxy(
          {},
          {
            get(_proxyTarget, methodProp: string | symbol) {
              if (typeof methodProp === 'symbol') return undefined;

              const endpointId = String(methodProp);

              return async (args?: CallArgs | Record<string, unknown>) => {
                const kebabEndpointId = endpointId
                  .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
                  .replace(/([A-Z]+)([A-Z][a-z0-9])/g, '$1-$2')
                  .replace(/_/g, '-')
                  .toLowerCase();

                let callArgs: CallArgs = { parameters: {}, headers: {} };

                if (args && typeof args === 'object' && !Array.isArray(args)) {
                  if ('parameters' in args || 'body' in args || 'headers' in args) {
                    callArgs = args as CallArgs;
                  } else {
                    callArgs = { parameters: args as Record<string, unknown> };
                  }
                }

                return target.call(providerId, kebabEndpointId, callArgs);
              };
            },
          },
        );
      },
    }) as ApinaClient;
  }

  /**
   * Initializes the SDK by querying the Apina registry providers endpoint.
   */
  async init(): Promise<void> {
    try {
      const response = await fetch(`${this.registryUrl}/api/v1/providers`);
      if (!response.ok) {
        throw new Error(`Failed to fetch providers: ${response.statusText}`);
      }
      const data = (await response.json()) as ProviderListResponse;
      for (const p of data.providers) {
        this.providers[p.id] = p;
      }
    } catch (error) {
      console.warn('ApinaClient failed to initialize:', error);
      throw error;
    }
  }

  /**
   * Executes a dynamic HTTP call through the Apina registry proxy gateway.
   *
   * @param {string} providerId - Identifier of the upstream provider.
   * @param {string} endpointId - Identifier of the endpoint to invoke.
   * @param {CallArgs} [args] - Structured parameters, body, and headers.
   * @returns {Promise<unknown>} The parsed response body from the registry.
   */
  async call(providerId: string, endpointId: string, args?: CallArgs): Promise<unknown> {
    const url = `${this.registryUrl}/api/v1/providers/${providerId}/endpoints/${endpointId}/call`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        parameters: args?.parameters || {},
        body: args?.body,
        headers: args?.headers || {},
      }),
    });

    const text = await response.text();
    let data: unknown;
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }

    if (!response.ok) {
      throw new Error(`Apina API call failed with status ${response.status}: ${typeof data === 'object' ? JSON.stringify(data) : data}`);
    }

    return data;
  }
}
