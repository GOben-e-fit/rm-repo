import { prisma } from '@/lib/db';

/**
 * Tenant-Resolver — leitet aus Domain (host header) oder Auth-Session die Tenant-ID ab.
 * F-Akte-Trennung: Operator-Rolle darf Cross-Tenant sehen, Endnutzer-Rolle nur den eigenen.
 */
export async function resolveTenantFromHost(host: string | null) {
  if (!host) return null;
  const domain = host.toLowerCase().split(':')[0];
  const tenant = await prisma.tenant.findFirst({ where: { domain } });
  return tenant;
}

export async function listAccessibleTenants(userId: string, isOperator: boolean) {
  if (isOperator) return prisma.tenant.findMany({ orderBy: { name: 'asc' } });
  return prisma.tenant.findMany({
    where: { memberships: { some: { userId } } },
    orderBy: { name: 'asc' },
  });
}
