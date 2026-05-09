import { prisma } from '@/lib/db.js';
import type { TenantContext } from '@/types/index.js';

/**
 * Registry liest aus DB welche MCP-Server + Tools für einen Tenant verfügbar sind.
 * Berücksichtigt Tenant-Scope (GLOBAL / PER_TENANT / WHITELIST).
 */
export async function findToolForInvocation(toolName: string, ctx: TenantContext) {
  const tool = await prisma.mcpTool.findFirst({
    where: {
      name: toolName,
      isActive: true,
      server: {
        isActive: true,
        OR: [
          { tenantScope: 'GLOBAL' },
          { tenantScope: 'WHITELIST', tenantIds: { has: ctx.tenantId } },
        ],
      },
    },
    include: { server: true },
  });
  return tool;
}

export async function listToolsForTenant(tenantId: string) {
  return prisma.mcpTool.findMany({
    where: {
      isActive: true,
      server: {
        isActive: true,
        OR: [
          { tenantScope: 'GLOBAL' },
          { tenantScope: 'WHITELIST', tenantIds: { has: tenantId } },
        ],
      },
    },
    include: { server: true },
    orderBy: [{ server: { name: 'asc' } }, { name: 'asc' }],
  });
}

export async function findFallbackForTool(toolName: string, tenantId: string) {
  // Tenant-spezifischer Fallback gewinnt vor Global-Fallback
  return prisma.fallbackMapping.findFirst({
    where: {
      toolName,
      isActive: true,
      OR: [{ tenantId }, { tenantId: null }],
    },
    orderBy: { tenantId: 'desc' }, // null kommt zuletzt
  });
}
