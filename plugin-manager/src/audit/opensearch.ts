import { ofetch } from 'ofetch';
import { env } from '@/lib/env.js';
import { logger } from '@/lib/logger.js';

export async function writeOpenSearchAudit(doc: Record<string, unknown>) {
  if (!env.OPENSEARCH_URL) return;
  try {
    await ofetch(`${env.OPENSEARCH_URL}/${env.OPENSEARCH_INDEX}/_doc`, {
      method: 'POST',
      body: doc,
      headers: env.OPENSEARCH_AUTH ? { Authorization: env.OPENSEARCH_AUTH } : {},
      timeout: 5000,
    });
  } catch (err) {
    logger.warn({ err: (err as Error).message }, 'opensearch-audit-failed');
  }
}
