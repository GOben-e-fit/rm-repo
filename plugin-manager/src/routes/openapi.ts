import { Hono } from 'hono';
import { listToolsForTenant } from '@/mcp/registry.js';
import { env } from '@/lib/env.js';

/**
 * OpenAPI-Wrapper für OpenWebUI Tool-Server-Integration.
 * OWUI ruft `/openapi/{tenant}/spec.json` ab und sieht alle Tools als OpenAPI 3.1 Operations.
 * OWUI ruft dann `/openapi/{tenant}/tools/{toolName}` als RPC-Endpoint auf.
 */
export const openapiRoutes = new Hono();

openapiRoutes.get('/openapi/:tenant/spec.json', async (c) => {
  const tenant = c.req.param('tenant');
  const tools = await listToolsForTenant(tenant);

  const spec = {
    openapi: '3.1.0',
    info: {
      title: `RM-KI Plugin Manager — Tools for tenant ${tenant}`,
      version: '0.0.1',
    },
    servers: [{ url: '/openapi' }],
    paths: Object.fromEntries(
      tools.map((t) => [
        `/${tenant}/tools/${t.name}`,
        {
          post: {
            summary: t.description ?? t.name,
            operationId: t.name,
            requestBody: {
              required: true,
              content: { 'application/json': { schema: t.inputSchema as object } },
            },
            responses: { '200': { description: 'OK' } },
          },
        },
      ]),
    ),
  };
  return c.json(spec);
});

openapiRoutes.post('/openapi/:tenant/tools/:toolName', async (c) => {
  // Bridge: leitet weiter an /v1/invoke mit User-Resolution aus Header
  const tenant = c.req.param('tenant');
  const toolName = c.req.param('toolName');
  const userId = c.req.header('x-user-id') ?? 'owui-anonymous';
  const apiKey = c.req.header('x-api-key');
  if (apiKey !== env.PLUGIN_MANAGER_API_KEY) {
    return c.json({ error: 'unauthorized' }, 401);
  }
  const args = (await c.req.json().catch(() => ({}))) as Record<string, unknown>;
  // Internal call (vermeidet HTTP-Roundtrip — TODO Phase 2.b: refactor invoke.ts to expose pure fn)
  const url = new URL(c.req.url);
  url.pathname = '/v1/invoke';
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': apiKey },
    body: JSON.stringify({ toolName, args, tenantId: tenant, userId }),
  });
  return c.json(await res.json(), res.status as 200);
});
