import { ofetch } from 'ofetch';
import { env } from '@/lib/env.js';
import { logger } from '@/lib/logger.js';

export async function writePaperclipEvidence(doc: Record<string, unknown>) {
  if (!env.PAPERCLIP_EVIDENCE_BRIDGE_URL) return;
  try {
    await ofetch(env.PAPERCLIP_EVIDENCE_BRIDGE_URL, {
      method: 'POST',
      body: doc,
      headers: env.PAPERCLIP_EVIDENCE_BRIDGE_KEY
        ? { 'x-evidence-key': env.PAPERCLIP_EVIDENCE_BRIDGE_KEY }
        : {},
      timeout: 5000,
    });
  } catch (err) {
    logger.warn({ err: (err as Error).message }, 'paperclip-evidence-failed');
  }
}
