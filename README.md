# rm-repo — RM-KI-Plattform Monorepo

**Akte:** 13 — Frontend Platform UI ([Akte-Pfad intern](https://example.local))
**Konzept:** [`FRONTEND-KONZEPT-2026-05-10.md`](https://example.local) (intern)
**Status:** Phase 1+2 Skelett (2026-05-10)

Mono-Repo für die zwei Hauptkomponenten der Frontend-Plattform der **RM-KI-Plattform** (DGX-basierte Multi-Tenant-KI-Plattform für ben-e-fit, ki-guru, medialine, busching, AlvI/R&M).

## Pakete

| Paket | Pfad | Stack | Phase | Zweck |
|---|---|---|---|---|
| **`rm-ki-operator-ui`** | [`operator-ui/`](operator-ui/) | Next.js 15 + React 19 + Tailwind v4 + Shadcn + AI SDK 6 + Anthropic SDK + Auth.js (Keycloak) + Prisma 6 | 1 | Cross-Tenant Operator-Dashboard: Container-Health, CP-Status, LiteLLM-Routing, Audits, Pentesting-Reporting, Computer-Use-Lite. **F-008-konforme Approvals.** |
| **`rm-ki-plugin-manager`** | [`plugin-manager/`](plugin-manager/) | Hono 4.7 + TypeScript 5.7 + Prisma 6 + `@modelcontextprotocol/sdk` + Pino + Zod | 2 | Zentraler MCP-Hub: registriert MCP-Server, brückt OpenAPI-Tools für OpenWebUI, Approval-Gate, Single Audit-Trail (OpenSearch + paperclip-evidence-bridge), **Dify als Fallback-Dispatcher**. |

## Architektur (3 Tracks, 1 Brücke)

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  OWUI ben-e-fit  │  │  OWUI ki-guru    │  │  OWUI medialine  │   ← Track 1 (Endnutzer)
│  + native Tools  │  │  + native Tools  │  │  + native Tools  │     OpenWebUI bleibt
│  + Theme-Fork    │  │  + Theme-Fork    │  │  + Theme-Fork    │     + Tools für
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘     Datenplatform/CLAW/
         │                     │                     │               Marketplace/Dify
         │                     │                     │
         └─────────────┬───────┴─────────────────────┘
                       │
                       ▼
          ┌─────────────────────────────┐
          │   plugin-manager  (Brücke)  │   ← OpenAPI-Wrapper für OWUI
          │   Hono + Prisma + Postgres  │     MCP-Client zu beliebigen MCPs
          │   Approval-Gate, Audit-Sink │     Dify-Fallback
          └────────────┬────────────────┘
                       │
         ┌─────────────┼─────────────────┐
         │             │                 │
         ▼             ▼                 ▼
    ┌────────┐   ┌──────────┐     ┌──────────────┐
    │ MCPs   │   │ OpenAPI  │     │ Dify         │
    │ Stripe │   │ Tools    │     │ Fallback     │
    │ GitHub │   │          │     │ Workflows    │
    │ Cloudfl│   │          │     │              │
    │ Postgr │   │          │     │              │
    │ Paper  │   │          │     │              │
    └────────┘   └──────────┘     └──────────────┘

                       ▲
                       │ pull-API (read) + Approval-RPC
                       │
              ┌────────┴─────────┐
              │  operator-ui     │   ← Track 2 (Operator/Plattform-Team)
              │  Next.js 15      │     Cross-Tenant-Dashboard
              │  Auth.js+Keycloak│     Computer-Use-Lite
              │  Tailscale-only  │     F-008 Approval-Workflows
              └──────────────────┘
```

## Lokales Setup

```bash
# Node 22+ und pnpm 10+ vorausgesetzt
git clone https://github.com/GOben-e-fit/rm-repo.git
cd rm-repo
pnpm install   # installiert beide Workspace-Pakete

# Beide parallel starten (zwei Terminals)
pnpm dev:ui      # http://localhost:3000  (Operator-UI)
pnpm dev:plugin  # http://localhost:4000  (Plugin-Manager)

# Tests / Lint / Typecheck (parallel über alle Pakete)
pnpm test:all
pnpm lint:all
pnpm typecheck:all
```

Pro Paket gibt es eine eigene `README.md` mit Detail-Setup ([operator-ui/README.md](operator-ui/README.md), [plugin-manager/README.md](plugin-manager/README.md)).

## Konventionen (HART — aus Akte rm-ki-plattform F-Regeln)

- **F-002:** Niemals Secret-Werte committen, in der UI sichtbar machen oder in Logs schreiben. `.env*`-Files sind ge-`.gitignore`-d.
- **F-008:** Runtime-Mutationen (Container-Restart, Provider-Switch, Secret-Rotate, etc.) brauchen **Approval-Gate** im Plugin-Manager + Approval-Modal in der Operator-UI. Kein direkter Apply ohne Zwei-Klick-Bestätigung + Audit-Log.
- **Tenant-Isolation:** Alle DB-Queries mit `tenantId` filtern (Postgres-RLS bevorzugt). Operator-Rolle darf cross-tenant; Endnutzer-Rolle nie.
- **Akten-Trennung:** Code in diesem Repo gehört zu Akte 13 (Frontend Platform UI). Off-Akte-Code (LiteLLM-Provider-Migration, n8n-Workflow-Inhalte, GAIA-Konfig, ...) gehört woanders.
- **Audit-Trail:** Jeder Tool-Call → OpenSearch + paperclip-evidence-bridge. Alle Mutationen → AuditEvent in Postgres + Sink-Spiegel.

## Hosting (Phase 1-3: nur intern via Tailscale)

- Operator-UI: `ops.spark-dev-01` (Tailscale-Hostname) — kein Cloudflared, kein Public-Exposure
- Plugin-Manager: nur DGX-internal Docker-Network erreichbar (Service `plugin-manager:4000`)
- Public-Exposure erst ab **Phase 4** (Whitelabel-Pilot AlvI/R&M) und nur mit Keycloak-MFA

## Roadmap (siehe Akte 13 TODO.md)

| Phase | Inhalt | Status |
|---|---|---|
| 0 | Konzept + Akte + Stack-Decisions | ✅ done |
| 1 | Operator-UI MVP (Read-only Dashboards) | 🔄 Skelett |
| 2 | Plugin-Manager-Service | 🔄 Skelett |
| 3 | Operator-UI Mutationen + Computer-Use-Lite (Playwright) | ⏸ pending |
| 4 | Whitelabel-Track + Pilot-Tenant AlvI/R&M | ⏸ pending |
| 5 | Bestand-Tenants schrittweise migrieren | ⏸ pending |
| 6 | Computer-Use Variante A (Native Anthropic, Sandbox) | ⏸ pending |
| Parallel | OpenWebUI native Tools/Functions/Pipes für Datenplattform/CLAW/Marketplace + Theme-Fork | ⏸ pending |
