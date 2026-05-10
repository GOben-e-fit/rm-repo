# Skills für Akte 14

> Stand: 2026-05-10. Kanonische Architektur-/Anforderungsquelle ist
> [`ARCHITECTURE-v2.md`](ARCHITECTURE-v2.md). Skills triggern automatisch,
> wenn Codex/Claude an KPI-Mining-Themen arbeitet.

## Akte-eigene Skills

Liegen unter `C:\Users\info\.codex\skills\` (Codex-Lookup) und werden bei
Mature-Status nach `rm-repo:skills/<skill>/` gespiegelt.

| Skill | Verwendung |
|---|---|
| `kpi-mining-product` | Produktstrategie, Roadmap, C-Level UX, Modulscope, Wettbewerb |
| `kpi-mining-ops` | Runtime, Routes, Container, Compose, Nginx, Cloudflare, Apply |
| `kpi-metric-contracts` | KPI-Definitionen, Reconciliation, dbt/Data-Contracts, Tests |
| `kpi-agent-runtime` | Agenten, LiteLLM-Routing, Langfuse, HITL, Replay, Audit |
| `kpi-market-intel` | Wettbewerb, Marktquellen, Benchmarks |
| `kpi-tenant-onboarding` | Tenant-Lifecycle, Keycloak, Buckets, Policies |
| `kpi-evals` | Eval-Sets, Replays, Akzeptanzkriterien pro Agent |

## Querschnitts-Skills

| Skill | Verwendung |
|---|---|
| `rm-ki-plattform` | Hauptregeln F-001..F-010, Boot-Pfad, Akten-Routing |
| `claude-migration-context` | Zugriff auf migrierte Claude-Snapshots (KPI-Marketing-Vorgänger) |
| `plattform-ops` | Allgemeine DGX-Plattform-Operations, Health-Checks |
| `competitive-intelligence` | Wettbewerbsanalysen außerhalb KPI |
| `source-management` | Quellen-Whitelisting, Crawling-Policies |
| `skill-creator` | Wenn neue KPI-Skills nachgezogen werden müssen |
| `cloudflare-tunnel` | Bei Tunnel-Themen (mit Akte-08 koordinieren) |
| `debug` | Bei Smoke-Failures |

## Plugins / Konnektoren

| Tool | Use Case | Akte-Bindung |
|---|---|---|
| Cloudflare API | Tunnel-Ingress lesen, DNS-Records | 08 (Mutation), 14 (read-only) |
| Browser Use / Playwright | Visuelle Smoke-Tests | 14 |
| GitHub | Repo-Status (falls Mirror aktiv) | 14 |
| Vercel | Vergleich gegen `mf-impulse-website.vercel.app/kpi-enterprise` | 14 (Quelle, nicht Ziel) |
| OpenRouter | Externe Modelle, nur policy-gated | 10 (Policy), 14 (Use) |
| OpenAI / Anthropic | Externe Modelle, nur policy-gated | 10, 14 |
| Crawl4AI | Web-Quellen-Onboarding | 03 (Engine), 14 (Use) |
| Nimble | Strukturierte Web-Daten | 14 |
| Airbyte | DB/SaaS-Konnektoren | 09, 14 |
| Trino | Federated SQL über Tenant-Quellen | 09 (Catalogs), 14 (Use) |
| ClickHouse | KPI-Time-Series, Events | 09 (Cluster), 14 (Schema) |
| OpenSearch + Qdrant | Hybrid-Suche für Semantic-Mapper | 09 (Cluster), 14 (Index) |
| OpenMetadata | Katalog/Lineage | 09 (Server), 14 (Schemas) |
| MinIO | Bronze/Silver/Gold pro Tenant | 09 (Cluster), 14 (Buckets) |
| LiteLLM | Modell-Routing pro Tenant | 10 (Policy), 14 (Use) |
| Langfuse | Trace + Eval | 10 (Server), 14 (Spans) |
| Keycloak | Auth + Tenant-Rollen | 10 (Server), 14 (Realms/Mapping) |
| n8n | Action-Workflows | 06 (Engine), 14 (Workflows) |
| Teams / Slack / Outlook / Gmail | Briefings + Maßnahmen | 14 (Connectors), 10 (Auth) |
| Dify | Optional als Plugin-Marketplace-Fallback | 13 (UI), 14 (Use) |
| Open WebUI | Operator-Konsole-Eingabe | 13, 14 |
