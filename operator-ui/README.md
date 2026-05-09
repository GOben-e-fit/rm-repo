# rm-ki-operator-ui

Operator-/Universal-Plattform-UI für die **RM-KI-Plattform**. Cross-Tenant-Dashboard für Plattform-Operator: Container-Health, CP-Status, LiteLLM-Routing, Audits, Pentesting-Reporting, Daten-Plane-Steuerung. F-008-konforme Approval-Workflows. Whitelabel-fähig.

Akte: [`G:\Meine Ablage\CODEX\project-launchpad\13-frontend-platform-ui\`](https://example.local) (intern)
Konzept: [`g:\Meine Ablage\codex\frontend-konzeption\FRONTEND-KONZEPT-2026-05-10.md`](https://example.local) (intern)

## Stack

- **Next.js 15** (App Router, RSC, Server Actions, Standalone Output)
- **React 19**, **TypeScript 5.7**
- **Tailwind CSS v4** + **Shadcn/ui** + **Radix Primitives**
- **Vercel AI SDK 6** + **@anthropic-ai/sdk** (für Computer-Use in Phase 6)
- **Auth.js v5** (Keycloak OIDC)
- **TanStack Query v5** + **Zustand**
- **Prisma 6** + **Postgres 17**
- **@modelcontextprotocol/sdk** (Plugin-Manager-Brücke)
- **Biome** (Lint/Format), **Vitest** (Unit), **Playwright** (E2E)

## Lokales Setup

```bash
# Prerequisites: Node 22+ und pnpm 10+ (lokal: Node 24.13 + pnpm 10.33 vorhanden)
pnpm install
cp .env.example .env.local
# .env.local befüllen — speziell DATABASE_URL und AUTH_KEYCLOAK_*

# Datenbank initial
pnpm db:generate
pnpm db:migrate  # erzeugt Schema in lokalem Postgres

# Dev server
pnpm dev   # http://localhost:3000

# Tests
pnpm typecheck
pnpm lint
pnpm test
pnpm test:e2e
```

## GitHub-Repo Setup (User-Action)

```bash
# 1. gh CLI installieren (falls nicht da)
winget install GitHub.cli
gh auth login   # GitHub-Account auswählen, Browser-Flow

# 2. Repo lokal initialisieren und remote anlegen
cd C:\Users\info\code\rm-ki-operator-ui
git init -b main
git add -A
git commit -m "feat: initial scaffold (Phase 1 MVP)"
gh repo create GOben-e-fit/rm-ki-operator-ui --private --source=. --push

# 3. (Optional) Branch-Schutz für main aktivieren
gh api -X PUT repos/GOben-e-fit/rm-ki-operator-ui/branches/main/protection \
  -F required_pull_request_reviews.required_approving_review_count=1 \
  -F enforce_admins=false
```

## Projekt-Layout

```
src/
├── app/
│   ├── layout.tsx          # Root Layout
│   ├── page.tsx            # → redirect /overview
│   ├── globals.css         # Tailwind v4 + Brand-Variablen
│   ├── (dashboard)/        # Layout-Gruppe für Operator-Sicht
│   │   ├── layout.tsx
│   │   ├── overview/       # Plattform-Health-Dashboard
│   │   ├── cp-status/      # SelfCLAW CP-Slices
│   │   ├── litellm/        # Provider-/Modell-Routing
│   │   ├── cloudflare/     # Public-Routes-Status
│   │   ├── containers/     # Container-Health pro Welle
│   │   └── audits/         # Audit-Events
│   └── api/
│       ├── auth/[...nextauth]/route.ts
│       └── health/route.ts
├── components/             # UI (Shadcn-Style)
├── lib/                    # auth, db, tenant, utils
└── server/                 # Server-side Clients (plugin-manager, ssh-bridge)

prisma/schema.prisma        # Tenant, User, Membership, AuditEvent
tests/unit/                 # Vitest
tests/e2e/                  # Playwright
```

## Konventionen (aus Akte 13)

- **F-002:** Secret-Werte niemals in der UI sichtbar (nur Masken `••••`, „Rotate"-Button)
- **F-008:** Runtime-Mutationen brauchen Approval-Modal mit Diff/Plan + Audit-Log
- **Tenant-Isolation:** Postgres-RLS + App-Layer-Filter; Operator-Rolle darf Cross-Tenant
- **Computer-Use-Audit:** jeder CU-Schritt → Screenshot + Tool-Call + Resultat → OpenSearch + paperclip-evidence-bridge

## Phase 1 ToDos (siehe Akte 13 TODO.md)

Read-only Dashboards, kein Mutation-Recht, nur intern via Tailscale erreichbar.
