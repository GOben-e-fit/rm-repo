/**
 * MCP-Client-Wrapper. In Phase 2 stub: ruft echo-Server lokal auf,
 * in Phase 2.b: nutzt @modelcontextprotocol/sdk für STDIO + HTTP-Transport.
 */
import type { McpServer, McpTool } from '@prisma/client';
import { logger } from '@/lib/logger.js';

export type McpInvokeArgs = {
  server: McpServer;
  tool: McpTool;
  args: Record<string, unknown>;
};

export async function invokeMcp({ server, tool, args }: McpInvokeArgs): Promise<unknown> {
  logger.info({ server: server.slug, tool: tool.name }, 'mcp.invoke');

  // Phase 2 stub: echo-Server gibt Args zurück, alle anderen → not implemented
  if (server.slug === 'echo') {
    return { echoed: args, ts: new Date().toISOString() };
  }

  // TODO Phase 2.b: integrate @modelcontextprotocol/sdk Client
  // - STDIO: spawn process and pipe JSON-RPC
  // - HTTP: REST/JSON-RPC over fetch
  // - WEBSOCKET: future
  throw new Error(`mcp-client: transport ${server.transport} not yet implemented`);
}
