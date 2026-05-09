import { PrismaClient } from '@prisma/client';
import { env } from './env.js';

declare global {
  // biome-ignore lint/style/noVar: required for global Prisma singleton in dev
  var __prisma: PrismaClient | undefined;
}

export const prisma =
  globalThis.__prisma ??
  new PrismaClient({
    log: env.NODE_ENV === 'development' ? ['warn', 'error'] : ['error'],
  });

if (env.NODE_ENV !== 'production') globalThis.__prisma = prisma;
