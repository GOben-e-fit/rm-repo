import { Hono } from 'hono';
import { listToolsForTenant } from '@/mcp/registry.js';

export const toolRoutes = new Hono();

toolRoutes.get('/v1/tools', async (c) => {
  const tenantId = c.req.query('tenant');
  if (!tenantId) return c.json({ error: 'tenant query param required' }, 400);
  const tools = await listToolsForTenant(tenantId);
  return c.json(
    tools.map((t) => ({
      name: t.name,
      description: t.description,
      requiresApproval: t.requiresApproval,
      server: t.server.slug,
    })),
  );
});
