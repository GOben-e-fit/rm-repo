/**
 * Mock-MCP-Server für Tests. Wird beim ersten Start in DB seed'ed (siehe seed-script).
 */
export const echoServerSeed = {
  slug: 'echo',
  name: 'Echo (Mock)',
  transport: 'STDIO' as const,
  endpoint: 'builtin://echo',
  tenantScope: 'GLOBAL' as const,
  isActive: true,
  tools: [
    {
      name: 'echo',
      description: 'Echoes back the args verbatim. Test/diagnostic tool.',
      inputSchema: {
        type: 'object',
        properties: { message: { type: 'string' } },
        required: ['message'],
      },
      requiresApproval: false,
    },
    {
      name: 'echo-with-approval',
      description: 'Like echo, but tagged approval-required for testing the approval gate.',
      inputSchema: {
        type: 'object',
        properties: { message: { type: 'string' } },
        required: ['message'],
      },
      requiresApproval: true,
    },
  ],
};
