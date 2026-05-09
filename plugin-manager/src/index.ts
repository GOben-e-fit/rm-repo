import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { env } from '@/lib/env.js';
import { logger } from '@/lib/logger.js';
import { healthRoutes } from '@/routes/health.js';
import { toolRoutes } from '@/routes/tools.js';
import { invokeRoutes } from '@/routes/invoke.js';
import { approvalRoutes } from '@/routes/approvals.js';
import { openapiRoutes } from '@/routes/openapi.js';

const app = new Hono();

// Auth-Middleware: x-api-key für /v1/* (OpenAPI hat eigene Logik im Handler)
app.use('/v1/*', async (c, next) => {
  const key = c.req.header('x-api-key');
  if (key !== env.PLUGIN_MANAGER_API_KEY) {
    return c.json({ error: 'unauthorized' }, 401);
  }
  await next();
});

app.route('/', healthRoutes);
app.route('/', toolRoutes);
app.route('/', invokeRoutes);
app.route('/', approvalRoutes);
app.route('/', openapiRoutes);

app.notFound((c) => c.json({ error: 'not-found', path: c.req.path }, 404));

app.onError((err, c) => {
  logger.error({ err: err.message, stack: err.stack }, 'unhandled-error');
  return c.json({ error: 'internal', message: err.message }, 500);
});

serve({ fetch: app.fetch, port: env.PORT, hostname: env.HOST }, (info) => {
  logger.info({ port: info.port, host: info.address }, 'rm-ki-plugin-manager listening');
});
