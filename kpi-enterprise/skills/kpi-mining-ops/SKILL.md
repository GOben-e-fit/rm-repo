---
name: kpi-mining-ops
description: Use for KPI Enterprise Mining runtime, DGX deployment, route recovery, Nginx, Cloudflare, container inventory, evidence bundles, health checks and rollback planning.
---

# KPI Mining Ops

Use this skill when work touches the KPI Enterprise Mining runtime, routes, containers,
domain mapping, Nginx config, Cloudflare, DGX deployment or operational evidence.

## Rules

- Treat `kpi.ben-e-fit.ai` as the canonical product domain and `kpi.medialine.app` as the operator/showcase domain unless the user changes that.
- Do not mutate live DGX/runtime routing without inventory, evidence, rollback path and explicit deploy intent.
- Follow SelfCLAW governance: preflight, scoped change, validation, evidence bundle, rollback note.
- Do not paste secrets from migrated logs or compose files into chat or docs.

## Workflow

1. Inventory local repo state first: `overrides/dev/kpi-mining`, compose service, Nginx config, OpenAPI and static API routes.
2. If old Claude/DGX context is needed, use `claude-migration-context` and search the index before reading raw files.
3. Verify route contract:
   - `/`
   - `/enterprise/`
   - `/api/health`
   - `/openapi.json`
   - `/api/v1/metric-definitions`
4. For DGX deploy, prefer a staged apply:
   - build container or mount override
   - test container locally
   - route one domain
   - validate browser desktop/mobile
   - capture evidence and rollback command

## Done Criteria

- Compose exposes the full KPI app directory, not only `index.html`.
- Healthcheck targets `/api/health`.
- Nginx serves static fallback JSON and proxies API misses to `agents-orchestrator:8000`.
- Evidence mentions exact status codes, routes tested and whether live routing was changed.
