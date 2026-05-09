import { z } from 'zod';

const schema = z.object({
  PORT: z.coerce.number().default(4000),
  HOST: z.string().default('0.0.0.0'),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  LOG_LEVEL: z.enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace']).default('info'),
  PLUGIN_MANAGER_API_KEY: z.string().min(16, 'API key must be at least 16 chars'),
  DATABASE_URL: z.string().url(),
  OPENSEARCH_URL: z.string().url().optional().or(z.literal('')),
  OPENSEARCH_INDEX: z.string().default('mcp-tool-invocations'),
  OPENSEARCH_AUTH: z.string().optional().or(z.literal('')),
  PAPERCLIP_EVIDENCE_BRIDGE_URL: z.string().url().optional().or(z.literal('')),
  PAPERCLIP_EVIDENCE_BRIDGE_KEY: z.string().optional().or(z.literal('')),
  DIFY_BASE_URL: z.string().url().optional().or(z.literal('')),
  DIFY_API_KEY: z.string().optional().or(z.literal('')),
  MCP_BUILTIN_ENDPOINTS: z.string().default(''),
});

export const env = schema.parse(process.env);
export type Env = z.infer<typeof schema>;
