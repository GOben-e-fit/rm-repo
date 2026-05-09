# rm-ki-plugin-manager

Zentraler **MCP-Hub** für die RM-KI-Plattform. Brückt zwischen Operator-UI / OpenWebUI / n8n und beliebigen MCP-Servern + OpenAPI-Tools. Setzt **Approval-Gates** (F-008-konform), schreibt **Single Audit-Trail** nach OpenSearch + paperclip-evidence-bridge. **Dify als Fallback-Dispatcher** wenn kein passendes Tool gefunden wird.

Akte: `G:\Meine Ablage\CODEX\project-launchpad\13-frontend-platform-ui\` (intern)

## Stack

- **Hono 4.7** auf **Node 22** (Bun-kompatibel falls später migriert)
- **TypeScript 5.7**
- **Prisma 6** + **Postgres 17**
- **@modelcontextprotocol/sdk 1.17**
- **Zod** für Env + Request-Validation
- **Pino** für strukturiertes JSON-Logging mit Secret-Redaction
- **Biome** + **Vitest**

## Endpoints (Phase 2)

| Methode | Pfad | Auth | Zweck |
|---|---|---|---|
| GET | `/health` | none | Liveness |
| GET | `/ready` | none | Readiness (DB-Ping) |
| GET | `/v1/tools?tenant=X` | x-api-key | Liste verfügbarer Tools für Tenant |
| POST | `/v1/invoke` | x-api-key | Tool aufrufen (mit Approval-Gate + Fallback) |
| GET | `/v1/approvals?tenant=X&status=PENDING` | x-api-key | Pending-Approvals listen |
| POST | `/v1/approvals/:id/decide` | x-api-key | Approval entscheiden (APPROVED/REJECTED) |
| GET | `/openapi/:tenant/spec.json` | none | OpenAPI 3.1 Spec für OWUI Tool-Server-Integration |
| POST | `/openapi/:tenant/tools/:toolName` | x-api-key | OWUI-bridged tool invocation |

## Lokales Setup

```bash
# Prerequisites: Node 22+ und pnpm 10+ (lokal: Node 24.13 + pnpm 10.33 vorhanden)
pnpm install
cp .env.example .env
# .env befüllen (mind. PLUGIN_MANAGER_API_KEY und DATABASE_URL)

# Postgres lokal starten (Beispiel mit Docker)
docker run -d --name pgmgr -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=plugin_manager -p 5432:5432 postgres:17-alpine

# Schema migrieren
pnpm db:generate
pnpm db:migrate

# Dev server
pnpm dev   # http://localhost:4000

# Smoke-Test
curl http://localhost:4000/health
curl -H "x-api-key: $PLUGIN_MANAGER_API_KEY" http://localhost:4000/v1/tools?tenant=test

# Tests
pnpm typecheck
pnpm lint
pnpm test
```

## GitHub-Repo Setup (User-Action)

```bash
# 1. gh CLI installieren falls nicht vorhanden
winget install GitHub.cli
gh auth login

# 2. Repo lokal initialisieren und remote anlegen
cd C:\Users\info\code\rm-ki-plugin-manager
git init -b main
git add -A
git commit -m "feat: initial scaffold (Phase 2 MVP)"
gh repo create GOben-e-fit/rm-ki-plugin-manager --private --source=. --push
```

## Architektur (Phase 2)

```
Operator-UI ──┐
              ├─→ POST /v1/invoke ──→ Approval-Gate ──→ MCP-Client ──→ MCP-Server
OWUI ─────────┤                                       │
n8n ──────────┘                                       └─→ Fallback ──→ Dify-Workflow

                                       ↓ jeder Schritt
                                  Audit-Sink:
                                  - OpenSearch (mcp-tool-invocations)
                                  - paperclip-evidence-bridge
```

## Phase 2 ToDos (siehe Akte 13 TODO.md)

- [x] Repo-Skelett, Routes, Schema, Echo-MCP Mock
- [ ] Postgres lokal/DGX einrichten + erste Migration
- [ ] Echo-MCP DB-seed-Script
- [ ] Tatsächliche `@modelcontextprotocol/sdk` Integration (STDIO + HTTP transport)
- [ ] Erste 5 echte MCPs einbinden: github, stripe, cloudflare, postgres-readonly, paperclip
- [ ] Dify-Fallback-Aufruf implementieren
- [ ] Pen-Test 2: Tenant-Isolation der Tool-Aufrufe
