# 14-kpi-enterprise-mining

Kanonische Akte für **KPI Enterprise Mining** als mandantenfähiges
C-Level Performance Operating System auf der DGX-Plattform.

Stand: 2026-05-10 (Spec-Bundle v2 materialisiert; CP-099 → CP-103 vorbereitend)

## Zweck

KPI Enterprise Mining ist kein Dashboard, sondern ein agentengestütztes
Steuerungssystem: KPI-Discovery, Metric Governance, Driver-Trees,
OKR-Lineage, Forecasting, Anomaly/RCA, C-Level-Briefings und
Action-Orchestration mit HITL-Approvals.

Diese Akte bündelt Produkt, Architektur, API, Agenten, Tenant-Contract,
Market-Intel, Runbooks und Tests an einer Stelle, **ohne** Runtime
zu ändern.

## Routing

- Produkt-Domain (Canonical): `kpi.ben-e-fit.ai`
- Operator/Showcase: `kpi.medialine.app`
- Sister-Tenant: `kpi.ki-guru.com`
- Tunnel: `spark-dev-01` Ingress `kpi.* → http://kpi-mining:80`
  (read-only verifiziert 2026-05-10).

## Grenzen

- Routing/Tunnel-Mutationen: **nur** in `08-dgx-cloudflare-routing`.
- Container-/Compose-/Volume-Mutationen: **nur** in `09-dgx-core-platform`
  via SelfCLAW-CP (offen: CP-099 KPI-Mining-Override-Governance).
- LiteLLM/Langfuse/Keycloak-Policies: **nur** in
  `10-dgx-litellm-langfuse-keycloak`.
- Tenant-Profile (ben-e-fit, ki-guru): **nur** in
  `11-ben-e-fit-ki-guru-tenants`.
- medialine.app Hero/UI/News: **nur** in `12-medialine-app`.
- Akten-Trennung F-003 strikt: keine Cross-Mutation hier.

## Schnellstart

- Neuer Codex-/Claude-Chat: [`START_NEW_CODEX_CHAT.md`](START_NEW_CODEX_CHAT.md) kopieren.
- **Volldokument (kanonisch):** [`ARCHITECTURE-v2.md`](ARCHITECTURE-v2.md) — Markt, Anforderungen, Backend, Repo, Roadmap, Aufwand.
- Produktverständnis: [`PRODUCT-SPEC.md`](PRODUCT-SPEC.md).
- System verstehen: [`ARCHITECTURE.md`](ARCHITECTURE.md).
- API-Vertrag: [`api/openapi.v1.yaml`](api/openapi.v1.yaml).
- Agent-Modell: [`agents/AGENT-TOPOLOGY.md`](agents/AGENT-TOPOLOGY.md).
- Mandanten-Modell: [`tenants/TENANT-ISOLATION-CONTRACT.md`](tenants/TENANT-ISOLATION-CONTRACT.md).
- Markteinordnung: [`market-intel/COMPETITIVE-ANALYSIS.md`](market-intel/COMPETITIVE-ANALYSIS.md).
- Runtime-Apply: [`runbooks/CP-099-kpi-mining-governance-package.md`](runbooks/CP-099-kpi-mining-governance-package.md).
- v1-Implementierung (lokal, noch nicht apply): [`../../.codex-work/cp075/overrides/dev/kpi-mining/`](../../.codex-work/cp075/overrides/dev/kpi-mining/).
- Governance-Preflight-Skript: [`../../_dgx_cp094_work/scripts/selfclaw_cp099_kpi_mining_integration_governance.py`](../../_dgx_cp094_work/scripts/selfclaw_cp099_kpi_mining_integration_governance.py).

## Skills (zu aktivieren)

Codex-Skills unter `C:\Users\info\.codex\skills\`:
- `kpi-mining-product` (Produkt-, Roadmap-, UX-Entscheidungen)
- `kpi-mining-ops` (Runtime, Routes, Container, Apply)
- `kpi-metric-contracts` (Definitionen, Reconciliation, Tests)
- `kpi-agent-runtime` (Agenten, Modell-Routing, HITL, Replay)
- `kpi-market-intel` (Wettbewerb, Quellen, Benchmarks)
- `kpi-tenant-onboarding` (Tenant-Lifecycle, Isolation)
- `kpi-evals` (Eval-Sets, Replays, Akzeptanzkriterien)
- Als Querschnitt: `claude-migration-context`, `rm-ki-plattform`,
  `plattform-ops`, `competitive-intelligence`, `source-management`.

## Status

- v1: Recovery + Cockpit + Demo-API + OpenAPI — **spezifiziert**, Apply
  via CP-099.
- v2: Echte Quellen (Airbyte/Nimble/Crawl4AI), Metric Store, Reports —
  spezifiziert, geplant ab CP-104.
- v3: Autonome Agenten, Benchmarks, Action-Workflows — spezifiziert,
  geplant ab CP-110.

## Implementiert (lokal lauffähig)

- `agents/orchestrator/` — FastAPI-Skelett mit allen v1-Routen,
  In-Memory-Tenant-Store, Demo-Auth via `X-Tenant-Id`. Tests:
  17/17 grün (smoke + tenant-deny).
  `pytest -v` aus dem Verzeichnis.
- `contracts/metric-contracts/` — JSON-Schema + 5 Beispiel-Contracts
  (MRR, Cash Runway, NPS, Sales Cycle, Order Backlog) + Validator-Skript.
- `infra/compose/docker-compose.dev.yml` — lokaler Dev-Stack
  (Orchestrator + Cockpit + Postgres + ClickHouse + MinIO).
- `.github/workflows/` — pytest, metric-contract-validate, openapi-validate
  (Spectral).
