# ARCHITECTURE — KPI Enterprise Mining

**Stand:** 2026-05-10 · abgeleitet aus [`ARCHITECTURE-v2.md`](ARCHITECTURE-v2.md) (Teil 3, 4)
**Owner:** Platform (kpi-mining-ops Skill)

> Engineering-Sicht. Produkt-Sicht in `PRODUCT-SPEC.md`. Detail- und
> Begründungs-Quelle bleibt `ARCHITECTURE-v2.md`.

---

## 1. Drei Planes

| Plane | Verantwortung | Schlüssel-Bausteine |
| --- | --- | --- |
| **App Plane** | UX, BFF, Auth-Edge | `kpi-mining` (Next.js + Fastify-BFF), `api-gateway` (:4001), Keycloak, n8n, Documenso, cost-proxy |
| **Agent Plane** | LLM-Orchestrierung, Tool-Calls, Eval | `agents-orchestrator` (FastAPI :8000), LangGraph, AutoGen Studio, CrewAI, Flowise, LiteLLM, Langfuse, graphrag-service, Letta, Presidio, generative-shield, Docling, Whisper, SearXNG, AnythingLLM |
| **Data Plane** | Ingest, Speicherung, Federation, Katalog | Airbyte, Crawl4AI/Nimble, MinIO (Bronze/Silver/Gold), Postgres, ClickHouse, Trino, dbt + Data Contracts, OpenMetadata, OpenSearch, Qdrant, Neo4j |

Vollständiges Mermaid-Diagramm: `ARCHITECTURE-v2.md §3.1`. Datenfluss-Sequenz: `§3.2`. RCA-Agent-Flow: `§3.3`.

## 2. Routing & Domains

| Domain | Zweck | Service-Ziel (im Tunnel `spark-dev-01`) |
| --- | --- | --- |
| `kpi.ben-e-fit.ai` | Canonical Produkt-Domain | `kpi-mining:80` |
| `kpi.medialine.app` | Operator/Showcase | `kpi-mining:80` (gleicher Container, anderer Brand) |
| `kpi.ki-guru.com` | Sister-Tenant | `kpi-mining:80` |
| `api.ben-e-fit.ai` | Public API v1 | `api-gateway:4001` |
| `auth.medialine.app` / `auth.ben-e-fit.ai` | Keycloak | `keycloak:8080` |
| `trace.medialine.app` | Langfuse | `langfuse-server:3000` |
| `n8n.medialine.app` | n8n Editor + Webhook | `n8n:5678` |
| `catalog.medialine.app` / `meta.medialine.app` | OpenMetadata | OpenMetadata-Server |
| `graph.medialine.app` | Neo4j Browser | Neo4j-Server |

Routing-Mutationen ausschließlich über Akte [`08-dgx-cloudflare-routing`](../08-dgx-cloudflare-routing/) (F-003).

## 3. Public API v1

Basis: `https://api.ben-e-fit.ai/v1/...`. Auth: Keycloak-JWT (Pflichtclaim `tenant_id`). RLS: `app.tenant`-Setting wird im Gateway aus dem JWT injiziert.

Endpunkt-Tabelle, Beispielschemas und Status-Codes: `ARCHITECTURE-v2.md §3.4`. Kanonisches OpenAPI-Artefakt: [`api/openapi.v1.yaml`](api/openapi.v1.yaml). Versionierung: SemVer auf Schema-Ebene; Breaking Changes nur als `/v2`.

## 4. Tenant-Isolation (Layer-Map)

| Layer | Mechanismus | Release-Gate |
| --- | --- | --- |
| Edge | CF Tunnel + WAF + JWT-Rate-Limit | Smoke pro Domain |
| Auth | Keycloak Realm pro Tenant | Realm-Diff-Check |
| Gateway | JWT verify + Inject `app.tenant` | Unit-Test |
| Postgres | RLS Policies `tenant_id = current_setting('app.tenant')` | Cross-Tenant-Deny |
| Trino | Catalog/Schema-Mapping + Rule-based ACL | Cross-Tenant-Deny |
| MinIO | Bucket-Prefix-Policy + tenant-bound STS | Cross-Tenant-Deny |
| ClickHouse | DB pro Tenant + Quotas | Cross-Tenant-Deny |
| Qdrant | Collection pro Tenant + API-Key | Cross-Tenant-Deny |
| OpenSearch | DLS Filter `tenant_id = X` | Cross-Tenant-Deny |
| Neo4j | Tenant-Property + RBAC-Procedures | Cross-Tenant-Deny |
| LiteLLM | Virtual Key pro Tenant + Quota + Tag | Trace-Audit |
| Presidio + Shield | PII/Toxicity Pre-/Post-LLM | Eval-Set |
| Langfuse | Project pro Tenant, Cross-Read off | Read-Test |
| Audit | ClickHouse `agent_runs_<tenant>` immutable, TTL 7y | Retention-Check |

Vollständiger Vertrag: [`tenants/TENANT-ISOLATION-CONTRACT.md`](tenants/TENANT-ISOLATION-CONTRACT.md).

## 5. SelfCLAW-Apply-Pattern (Übersicht)

```
proposal → evidence → approval → snapshot → apply → smoke → audit
                                       ↓
                                    rollback (wenn smoke fail)
```

Anwendung im KPI-Kontext:
- **Metric Contract Promote**: PR + dbt-Manifest-Diff + Approver ≥ 2 + Snapshot der `metric_definitions`-Vorzeile + Apply + Smoke (kpi_observations referenzieren neue Version) + Audit.
- **Action-Run**: Vorschlag + Evidence-Bundle + Approver + Pre-Snapshot des Ziel-Systems + Execute via n8n + Post-Smoke + Audit.
- **Compose/Container-Apply** (KPI-Service): siehe [`runbooks/CP-099-kpi-mining-governance-package.md`](runbooks/CP-099-kpi-mining-governance-package.md).

## 6. Hybrid-LLM-Policy

Default: lokal (Qwen3 / Llama3 via Ollama hinter LiteLLM). Externer Cloud-Call nur, wenn:

1. Datenklassifikation ∈ `{public, anonymized}`,
2. Aufgabentyp im Skill-Manifest erlaubt `external = true`,
3. PII-Scan (Presidio) zeigt **kein** Hit,
4. Tenant-Policy erlaubt externe Models,
5. Quota im LiteLLM Virtual Key reicht.

Bei jedem Veto → Block + Fallback lokal + Audit-Eintrag mit Reason.

## 7. Compose-Overlay-Pattern (DGX)

```
/opt/medialine/compose.yml          # root-owned Plattform-Kern
/srv/rm-repo/infra/compose/compose.override.yml   # User-owned Repo-Sync
                ↓
docker compose -f /opt/medialine/compose.yml \
               -f /srv/rm-repo/infra/compose/compose.override.yml \
               up -d
```

Begründung: Plattform-Admins schützen den Kern; Produkt-Teams iterieren ohne sudo.

## 8. CI/CD (Highlights)

- Pfad-basierte Trigger (`apps/kpi-mining/**`, `contracts/dbt/**`, `skills/**`, `infra/cloudflare/**`).
- Stufen: Lint → Unit → Contract → **Tenant-Deny** → Agent-Replay → dbt → OpenAPI Schemathesis → Playwright → Image-Build → Deploy mit Approval.
- Trunk-based, `main` immer deploy-fähig. Promotion Dev → Staging → Prod mit Required Reviewers ≥ 2 in Prod-Environment.
- Vollständige Workflow-Liste: `ARCHITECTURE-v2.md §4.3`.

## 9. Beobachtbarkeit & Kostenkontrolle

- Container-/Service-Metriken: Prometheus → Grafana, Logs → Loki, Traces → Tempo, Synthetic → Uptime Kuma.
- LLM-Kosten: cost-proxy aggregiert pro Tenant + Modell, Alerts bei 80 %/100 % Quota.
- Audit-Volume: ClickHouse `agent_runs_<tenant>` mit TTL-Policy; Sampling für Langfuse-Cost-Containment, **vollständige** Pflichtdaten (Approval, Evidence-URI, Tool-Args) niemals samplen.

## 10. Risiko-Matrix (Kurzform)

| ID | Risiko | Mitigation |
| --- | --- | --- |
| R-01 | Cross-Tenant-Leak via Agent-State | Tenant-Tag im State, Deny-Tests release-blocking |
| R-02 | LLM-Halluzination → falsche KPI-Definition | Metric Contracts Pflicht, HITL Promote |
| R-03 | Cloud-LLM erhält PII | Presidio + Policy-Gate, Default deny |
| R-04 | EU AI Act Non-Compliance | Compliance-Agent + FRIA-Templates |
| R-05 | DGX-SPOF | 2. DGX als Hot-Standby via Tailscale |
| R-06 | dbt verändert KPI-Semantik unbemerkt | Data Contracts + Datafold-Diff in CI |
| R-07 | Auto-Apply schadet | SelfCLAW: kein auto-apply, Approval + Rollback |
| R-08 | Performance < SLO bei > 50 Tenants | ClickHouse Sharding + Trino Worker + Cube Pre-Agg |
| R-09 | Wettbewerber kopiert On-Prem-Story | Tempo (v3 in 90d) + Vertical-Templates |
| R-10 | LLM-Kosten unkontrolliert | LiteLLM Quota + cost-proxy + Alerts |

Volldetails: `ARCHITECTURE-v2.md §3.6`.

## 11. Repo-Strategie (Kurzform)

**Mono-Repo `rm-repo`** mit klaren Top-Level-Bereichen: `apps/`, `agents/`, `skills/`, `contracts/`, `infra/`, `runbooks/`, `evidence/`, `evals/`, `secrets/`, `docs/`. Begründung + Vollstruktur: `ARCHITECTURE-v2.md §4.1, §4.2`.

Skill-Pfad innerhalb Repo: `skills/<skill-name>/{skill.yaml,prompts/,tools/,eval/,README.md}`. Lokale Codex-Skills unter `C:/Users/info/.codex/skills/<name>/SKILL.md` werden bei Mature-Status ins Repo gespiegelt (siehe [`SKILLS.md`](SKILLS.md)).
