import { zValidator } from '@hono/zod-validator';
import { Hono } from 'hono';
import { prisma } from '@/lib/db.js';
import { logger } from '@/lib/logger.js';
import { writeOpenSearchAudit } from '@/audit/opensearch.js';
import { writePaperclipEvidence } from '@/audit/paperclip-evidence.js';
import { invokeMcp } from '@/mcp/client.js';
import { findFallbackForTool, findToolForInvocation } from '@/mcp/registry.js';
import { ToolInvocationRequest } from '@/types/index.js';

export const invokeRoutes = new Hono();

invokeRoutes.post('/v1/invoke', zValidator('json', ToolInvocationRequest), async (c) => {
  const req = c.req.valid('json');
  const ctx = { tenantId: req.tenantId, userId: req.userId };

  // 1. Tool lookup
  const tool = await findToolForInvocation(req.toolName, ctx);

  // 2. Kein Tool gefunden → Fallback?
  if (!tool) {
    const fallback = await findFallbackForTool(req.toolName, ctx.tenantId);
    if (fallback) {
      logger.info({ toolName: req.toolName, dify: fallback.difyWorkflowId }, 'fallback-to-dify');
      // TODO Phase 2.b: actually call Dify workflow
      const inv = await prisma.toolInvocation.create({
        data: {
          serverId: 'fallback', // pseudo — TODO: dedicated fallback-server placeholder
          toolName: req.toolName,
          tenantId: ctx.tenantId,
          userId: ctx.userId,
          args: req.args,
          status: 'FALLBACK_TO_DIFY',
        },
      }).catch(() => null);
      return c.json({
        ok: false,
        error: 'no-direct-tool, fallback-to-dify',
        fallback: { kind: 'dify', workflowId: fallback.difyWorkflowId },
        invocationId: inv?.id,
      });
    }
    return c.json({ ok: false, error: 'no-tool-and-no-fallback', toolName: req.toolName }, 404);
  }

  // 3. Approval-Gate
  if (tool.requiresApproval && !req.approvalToken) {
    const expiresAt = new Date(Date.now() + 1000 * 60 * 30); // 30 min
    const approval = await prisma.approvalRequest.create({
      data: {
        toolName: req.toolName,
        args: req.args,
        tenantId: ctx.tenantId,
        requestedBy: ctx.userId,
        expiresAt,
      },
    });
    return c.json({
      ok: false,
      error: 'approval-required',
      needsApproval: { requestId: approval.id, expiresAt: expiresAt.toISOString() },
    });
  }

  // 4. Validate approvalToken if provided
  if (req.approvalToken) {
    const approval = await prisma.approvalRequest.findUnique({ where: { id: req.approvalToken } });
    if (!approval || approval.status !== 'APPROVED') {
      return c.json({ ok: false, error: 'approval-invalid-or-not-approved' }, 403);
    }
    if (approval.expiresAt < new Date()) {
      return c.json({ ok: false, error: 'approval-expired' }, 403);
    }
  }

  // 5. Create invocation row
  const invocation = await prisma.toolInvocation.create({
    data: {
      serverId: tool.serverId,
      toolId: tool.id,
      toolName: tool.name,
      tenantId: ctx.tenantId,
      userId: ctx.userId,
      args: req.args,
      status: 'RUNNING',
      approvalRequestId: req.approvalToken,
    },
  });

  // 6. Invoke MCP
  try {
    const result = await invokeMcp({ server: tool.server, tool, args: req.args });
    const finished = await prisma.toolInvocation.update({
      where: { id: invocation.id },
      data: { status: 'SUCCESS', result: result as object, finishedAt: new Date() },
    });

    // 7. Audit
    const auditDoc = {
      invocationId: finished.id,
      tenantId: ctx.tenantId,
      userId: ctx.userId,
      toolName: tool.name,
      server: tool.server.slug,
      status: 'SUCCESS',
      ts: new Date().toISOString(),
    };
    await Promise.all([writeOpenSearchAudit(auditDoc), writePaperclipEvidence(auditDoc)]);

    return c.json({ ok: true, data: result, auditId: finished.id, invocationId: finished.id });
  } catch (err) {
    await prisma.toolInvocation.update({
      where: { id: invocation.id },
      data: {
        status: 'FAILED',
        finishedAt: new Date(),
        errorMessage: (err as Error).message,
      },
    });
    return c.json({ ok: false, error: (err as Error).message }, 500);
  }
});
