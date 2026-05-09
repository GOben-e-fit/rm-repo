import { Hono } from 'hono';
import { prisma } from '@/lib/db.js';

export const healthRoutes = new Hono();

healthRoutes.get('/health', (c) =>
  c.json({ status: 'ok', service: 'rm-ki-plugin-manager', ts: new Date().toISOString() }),
);

healthRoutes.get('/ready', async (c) => {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return c.json({ status: 'ready', db: 'ok' });
  } catch (err) {
    return c.json({ status: 'not-ready', db: (err as Error).message }, 503);
  }
});
