import { PrismaClient } from '@prisma/client';

declare global {
  // biome-ignore lint/style/noVar: required for global Prisma singleton in dev
  var __prisma: PrismaClient | undefined;
}

export const prisma =
  globalThis.__prisma ?? new PrismaClient({ log: ['warn', 'error'] });

if (process.env.NODE_ENV !== 'production') globalThis.__prisma = prisma;
