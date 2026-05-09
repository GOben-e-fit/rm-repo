import { Hono } from 'hono';
import { z } from 'zod';
import { zValidator } from '@hono/zod-validator';
import { prisma } from '@/lib/db.js';

export const approvalRoutes = new Hono();

approvalRoutes.get('/v1/approvals', async (c) => {
  const tenantId = c.req.query('tenant');
  const status = (c.req.query('status') ?? 'PENDING') as
    | 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED';
  const where = tenantId ? { tenantId, status } : { status };
  const items = await prisma.approvalRequest.findMany({
    where,
    orderBy: { createdAt: 'desc' },
    take: 100,
  });
  return c.json(items);
});

const Decision = z.object({
  decision: z.enum(['APPROVED', 'REJECTED']),
  reviewerId: z.string().min(1),
  reason: z.string().optional(),
});

approvalRoutes.post('/v1/approvals/:id/decide', zValidator('json', Decision), async (c) => {
  const id = c.req.param('id');
  const { decision, reviewerId, reason } = c.req.valid('json');
  const updated = await prisma.approvalRequest.update({
    where: { id },
    data: { status: decision, reviewedBy: reviewerId, reason, decidedAt: new Date() },
  });
  return c.json(updated);
});
