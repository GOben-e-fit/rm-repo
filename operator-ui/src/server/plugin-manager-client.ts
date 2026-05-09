/**
 * Client für den Plugin-Manager-Service (rm-ki-plugin-manager).
 * Wird von Server Components / Server Actions in der Operator-UI aufgerufen.
 */

const BASE = process.env.PLUGIN_MANAGER_BASE_URL ?? 'http://plugin-manager:4000';
const API_KEY = process.env.PLUGIN_MANAGER_API_KEY ?? '';

export type ToolInvocation = {
  toolName: string;
  args: Record<string, unknown>;
  tenantId: string;
  userId: string;
  approvalToken?: string;
};

export type ToolResult =
  | { ok: true; data: unknown; auditId: string }
  | { ok: false; error: string; needsApproval?: { requestId: string } };

export async function invokeTool(req: ToolInvocation): Promise<ToolResult> {
  const res = await fetch(`${BASE}/v1/invoke`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': API_KEY,
      'x-tenant-id': req.tenantId,
      'x-user-id': req.userId,
    },
    body: JSON.stringify(req),
  });
  if (!res.ok) return { ok: false, error: `plugin-manager ${res.status}` };
  return (await res.json()) as ToolResult;
}

export async function listTools(tenantId: string) {
  const res = await fetch(`${BASE}/v1/tools?tenant=${encodeURIComponent(tenantId)}`, {
    headers: { 'x-api-key': API_KEY },
  });
  if (!res.ok) return [];
  return (await res.json()) as Array<{
    name: string;
    description: string;
    requiresApproval: boolean;
    server: string;
  }>;
}
