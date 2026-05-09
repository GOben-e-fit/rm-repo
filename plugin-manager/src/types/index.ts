import { z } from 'zod';

export const ToolInvocationRequest = z.object({
  toolName: z.string().min(1),
  args: z.record(z.unknown()).default({}),
  tenantId: z.string().min(1),
  userId: z.string().min(1),
  approvalToken: z.string().optional(),
});
export type ToolInvocationRequest = z.infer<typeof ToolInvocationRequest>;

export type ToolInvocationResult =
  | { ok: true; data: unknown; auditId: string; invocationId: string }
  | {
      ok: false;
      error: string;
      needsApproval?: { requestId: string; expiresAt: string };
      fallback?: { kind: 'dify'; workflowId: string };
    };

export type TenantContext = {
  tenantId: string;
  userId: string;
};
