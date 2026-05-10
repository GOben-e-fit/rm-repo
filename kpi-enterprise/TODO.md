# Akte 14 TODO — KPI Enterprise Mining

**Stand:** 2026-05-10 · v2-Spec aktiv ([`ARCHITECTURE-v2.md`](ARCHITECTURE-v2.md))

> Phasen entsprechen `ARCHITECTURE-v2.md §5` (90-Tage-Roadmap).
> Aufwand siehe `§6` (~73 FTE-Wochen, 5–6 FTE × 13 Wochen).

## Phase v1 — Cockpit-Stabilisierung (CP-099 → CP-103, W1–W4)

- [x] Akte-14 Spec-Bundle materialisieren
  - [x] [`ARCHITECTURE-v2.md`](ARCHITECTURE-v2.md) (User-Input vom 2026-05-09)
  - [x] [`PRODUCT-SPEC.md`](PRODUCT-SPEC.md)
  - [x] [`ARCHITECTURE.md`](ARCHITECTURE.md)
  - [x] [`api/openapi.v1.yaml`](api/openapi.v1.yaml)
  - [x] [`agents/AGENT-TOPOLOGY.md`](agents/AGENT-TOPOLOGY.md)
  - [x] [`tenants/TENANT-ISOLATION-CONTRACT.md`](tenants/TENANT-ISOLATION-CONTRACT.md)
  - [x] [`market-intel/COMPETITIVE-ANALYSIS.md`](market-intel/COMPETITIVE-ANALYSIS.md)
  - [x] [`runbooks/CP-099-kpi-mining-governance-package.md`](runbooks/CP-099-kpi-mining-governance-package.md)

- [ ] **CP-099** Inventar + Governance auf DGX (no-apply)
  - Run [`_dgx_cp094_work/scripts/selfclaw_cp099_kpi_mining_integration_governance.py`](../../_dgx_cp094_work/scripts/selfclaw_cp099_kpi_mining_integration_governance.py) `--write-current` auf `spark-dev-01`
  - Output: `selfclaw/evidence/kpi-mining-integration-governance.current.json` etc.
  - File-Klassifikations-CSV (`evidence/cp099/file-classification.csv`)
  - Vertrags-Definition für OpenMetadata/OpenSearch/Trino/LiteLLM/Tenant Plane

- [ ] **CP-100** Cockpit-UI Replace `/`, `/enterprise/`, `/console`, `/tools`
  - Übernahme der v1-Materialisierung aus [`.codex-work/cp075/overrides/dev/kpi-mining/`](../../.codex-work/cp075/overrides/dev/kpi-mining/)
  - Brand-Switch via `data-brand` (ben-e-fit / ki-guru / medialine)
  - Cockpit zeigt 5 Spalten: Was passiert / Warum / Was tun / Owner / Evidenz

- [ ] **CP-101** Static `/api/v1/*` + OpenAPI-Mount für Smoke + Demo
  - OpenAPI v1 als `/openapi.json` und `/openapi.yaml`
  - 13 Demo-Endpoints aus [`api/openapi.v1.yaml`](api/openapi.v1.yaml) statisch verfügbar

- [ ] **CP-102** Healthcheck-Smoke + Cloudflare Per-Path-Status klassifizieren (F-009)
  - Pre/Post-Smoke-Skripte, Brand-DOM-Check je Domain

- [ ] **CP-103** Evidence-Bundle + Apply via Wartungsfenster
  - Approver ≥ 2 + DGX-Owner + Wartungsfenster
  - Pre-Apply-Smoke grün, Post-Apply-Smoke grün, Rollback ready

- [ ] **Tenant-Deny-Test-Harness** (release-blocking)
  - 2 Test-Tenants `tnt_test_a` / `tnt_test_b`
  - Cross-Tenant-Read-Tests gegen Postgres/Trino/MinIO/CH/Qdrant/OS/Neo4j/Langfuse

## Phase v2 — Echte Datenquellen + KPI-Mining (CP-104 → CP-110, W5–W9)

- [ ] **CP-104** `agents-orchestrator` Service-Skeleton (FastAPI :8000, OpenAPI v1)
- [ ] **CP-105** Quell-Onboarding (Airbyte für strukturiert, Nimble + Crawl4AI für Web)
- [ ] **CP-106** Metric Store Schema in ClickHouse + dbt-Modelle
- [ ] **CP-107** Trino-Federation für Tenant-Sources (read-only erst)
- [ ] **CP-108** OpenMetadata-Lineage für Metric-Definitionen + Sources
- [ ] **CP-109** Hybrid-Search (OpenSearch BM25 + Qdrant Vector) für Semantic-Mapper
- [ ] **CP-110** Tenant-Isolation-Negative-Tests (analog CP-073) für KPI-Pfade

**Phase-Akzeptanz:** 1 Pilot-Mandant zeigt 25+ echte KPIs, Driver-Tree mit ≥ 30 Knoten, mind. 1 Anomalie pro Woche detektiert.

## Phase v3 — Autonome Agenten + HITL (CP-111 → CP-120, W10–W13)

- [ ] **CP-111** KPI-Miner-Agent (Schema-Profiling → Candidate-KPIs)
- [ ] **CP-112** Driver-Tree-Agent + Canvas
- [ ] **CP-113** Anomaly/RCA-Agent (Robust-Z, STL, Causal-Hint)
- [ ] **CP-114** C-Level-Briefing-Agent (Was/Warum/Was-tun/Owner/Evidenz)
- [ ] **CP-115** ROI/Monte-Carlo-Agent
- [ ] **CP-116** Action-Orchestrator (n8n-Trigger, Teams/Slack/Outlook)
- [ ] **CP-117** Benchmark-Agent (öffentliche Quellen + Branchenfeeds)
- [ ] **CP-118** Compliance/Audit-Agent (EU-AI-Act-Trail, Replay)
- [ ] **CP-119** HITL-Approval-Flow + Langfuse-Integration
- [ ] **CP-120** Eval-Set & Replay-Pipeline für alle Agenten

**Phase-Akzeptanz:** täglicher CFO-Briefing geht raus, mind. 1 HITL-Maßnahme abgewickelt, Compliance-Dossier Q2/2026 generiert.

## Querschnitt

- [ ] `kpi-mining-product` Skill mit konkreten Decision-Templates füllen
- [ ] `kpi-evals` Skill mit Eval-Definitionen pro Agent (siehe [`agents/AGENT-TOPOLOGY.md §5`](agents/AGENT-TOPOLOGY.md))
- [ ] Stripe/Pricing-Modell finalisieren (siehe [`PRODUCT-SPEC.md §8`](PRODUCT-SPEC.md))
- [ ] AVV-/Datenschutz-Vorlagen pro Tenant
- [ ] EU-AI-Act-Risk-Klassifikation pro Agent dokumentieren
- [ ] rm-repo Mono-Repo-Struktur bootstrappen (siehe [`ARCHITECTURE-v2.md §4.2`](ARCHITECTURE-v2.md))
- [ ] CI/CD-Workflows (siehe [`ARCHITECTURE-v2.md §4.3`](ARCHITECTURE-v2.md))

## Offene Entscheidungen für User

1. **Pilot-Tenant für v1**: medialine intern? AlvI/R&M? ben-e-fit?
2. **Pricing-Modell**: Pro-Tenant Flatrate, Pro-User, Pro-Metric-Volume, Hybrid mit Setup-Fee?
3. **Datenschutz-Default für externe Modelle**: deny-all (nur lokal) oder per-Tenant-Opt-in für anonymisierte Pfade?
4. **CP-099 Wartungsfenster**: vor oder nach Akte-13 Phase-0-Pilot?
5. **Brand-Hierarchie kanonisch**: ben-e-fit Hauptmarke / medialine Showcase / ki-guru Sister — oder umsortieren?
6. **rm-repo-Bootstrap**: bestehendes `rm-repo` umstrukturieren oder als Greenfield neu anlegen?

## Verweis auf existierende Artefakte

- v1-Materialisierung lokal (Codex-Hand): [`.codex-work/cp075/overrides/dev/kpi-mining/`](../../.codex-work/cp075/overrides/dev/kpi-mining/) — UI-Shell + Demo-API + OpenAPI-Stub + Tests + Compose-Override + Evidence-Screenshots
- Governance-Preflight-Skript (Codex-Hand): [`_dgx_cp094_work/scripts/selfclaw_cp099_kpi_mining_integration_governance.py`](../../_dgx_cp094_work/scripts/selfclaw_cp099_kpi_mining_integration_governance.py)
- DGX-Origin (uncommitted Override): `/opt/rm-ki-appliance/repo/overrides/dev/kpi-mining/` auf `spark-dev-01`
- Vorgänger Claude-Hand: [`claude-migration/.../local_901c334f.../outputs/kpi-mining-index.html`](../../claude-migration/generated-outputs/a3a9d2b0-d35a-45ce-85c6-95cd0381296c/8b7a6081-325b-421d-bffd-fbdd9a1a6f8b/local_901c334f-3106-44b2-a7a0-68543ee63fad/outputs/kpi-mining-index.html) — 308 Zeilen statische Marketing-Seite
