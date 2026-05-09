import { describe, expect, it, vi } from 'vitest';

vi.mock('@/lib/env.js', () => ({
  env: {
    PLUGIN_MANAGER_API_KEY: 'test-key-1234567890',
    NODE_ENV: 'test',
    LOG_LEVEL: 'error',
    OPENSEARCH_INDEX: 'mcp',
    OPENSEARCH_URL: '',
    PAPERCLIP_EVIDENCE_BRIDGE_URL: '',
  },
}));

vi.mock('@/lib/db.js', () => ({
  prisma: {
    mcpTool: { findFirst: vi.fn() },
    fallbackMapping: { findFirst: vi.fn() },
    approvalRequest: { create: vi.fn(), findUnique: vi.fn() },
    toolInvocation: { create: vi.fn(), update: vi.fn() },
  },
}));

import { findToolForInvocation } from '@/mcp/registry.js';

describe('registry stub', () => {
  it('exists', () => {
    expect(typeof findToolForInvocation).toBe('function');
  });
});
