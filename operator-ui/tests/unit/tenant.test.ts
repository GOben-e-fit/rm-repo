import { describe, expect, it, vi } from 'vitest';

vi.mock('@/lib/db', () => ({
  prisma: {
    tenant: {
      findFirst: vi.fn(async ({ where }) =>
        where.domain === 'chat.ben-e-fit.ai'
          ? { id: 't1', slug: 'ben-e-fit', name: 'Ben-e-fit', domain: 'chat.ben-e-fit.ai' }
          : null,
      ),
    },
  },
}));

import { resolveTenantFromHost } from '@/lib/tenant';

describe('resolveTenantFromHost', () => {
  it('strips port and lowercases', async () => {
    const t = await resolveTenantFromHost('Chat.Ben-e-fit.AI:3000');
    expect(t?.slug).toBe('ben-e-fit');
  });

  it('returns null for unknown host', async () => {
    const t = await resolveTenantFromHost('unknown.example.com');
    expect(t).toBeNull();
  });

  it('returns null for empty host', async () => {
    const t = await resolveTenantFromHost(null);
    expect(t).toBeNull();
  });
});
