# AGENT-TOPOLOGY — KPI Enterprise Mining

**Stand:** 2026-05-10 · abgeleitet aus [`../ARCHITECTURE-v2.md`](../ARCHITECTURE-v2.md) (§2.1 FR-01 bis FR-13, §3.3)
**Owner:** Agents (kpi-agent-runtime Skill)

> Dieses Dokument beschreibt die Agent-Population, ihre Verantwortlichkeiten,
> Tool-Bindings, Modell-Routing-Default und Eval-Hooks. Quelle der Wahrheit
> bleibt `ARCHITECTURE-v2.md`. Eval-Definitionen leben in
> `kpi-evals` Skill und `evals/` im rm-repo.

---

## 1. Agent-Liste (10 Agenten in 4 Tiers)

| Tier | Agent | Typ | Trigger | Modell-Default | External Allowed |
| --- | --- | --- | --- | --- | --- |
| Mining | KPI-Discovery | LangGraph | Source-Sync, manuell | qwen3-72b-local | nein |
| Mining | Data-Profiler | Python+LLM | Source-Sync | local | nein |
| Mining | Semantic-Mapper | LangGraph | nach Profiler | local | nein |
| Insight | Anomaly-Detector | Python (kein LLM) | Cron pro Metric | – | – |
| Insight | RCA | CrewAI (Researcher+Quant+Reporter) | Anomaly-Event | local primary, fallback Cloud (anonymisiert) | bedingt |
| Insight | Forecasting | Python+GBT/GPU | Cron, manuell | – | nein |
| Action | Briefing-Generator | LangGraph | Cron daily/weekly/monthly | local | bedingt (nur Branding-Polish) |
| Action | Benchmark | LangGraph + Crawl4AI/Nimble | Cron, manuell | local + external (nur Public-Quellen) | ja |
| Action | Action-Orchestrator | n8n + LangGraph Wrapper | Insight-Approval | – | – |
| Compliance | Compliance-Auditor | LangGraph + Documenso | Cron quarterly | local | nein |

## 2. Verantwortlichkeiten im Detail

### 2.1 Mining-Tier

**KPI-Discovery (FR-01).** Liest Schema + Spalten-Statistik + Sample aus Trino, paart mit OpenMetadata-Tags und Letta-Memory (frühere Discovery-Runs des Tenants), schlägt Kandidaten-KPIs mit Score, Begründung, SQL vor. Persistiert nach `kpi_candidates`. Akzeptanz: ≥ 25 Kandidaten in 30 Min auf 1 ERP + 1 CRM, ≥ 60 % Review-Akzeptanz.

**Data-Profiler.** Berechnet Spalten-Profile (null_ratio, distinct_count, sample_values, detected_pii via Presidio). Output → OpenMetadata + `dataset_profiles`-Tabelle. Kein LLM für die Profile selbst, nur für Naming-Hints.

**Semantic-Mapper.** Mappt Datensätze auf Domain-Konzepte (finance, sales, ops, hr, supply-chain). Vergleicht Spaltennamen + Tags + Heuristiken gegen domain-spezifische Templates aus `kpi-mining-product` Skill.

### 2.2 Insight-Tier

**Anomaly-Detector (FR-06, ohne LLM).** Methoden pro Metric Contract konfigurierbar: STL+RobustZ, Prophet-Residual, Isolation Forest. Schreibt Events in `kpi_observations.anomaly_events`. Performance-Ziel: < 30s pro 10k-Punkte-Reihe.

**RCA (FR-06, CrewAI).** Drei Rollen:
- **Researcher** — traversiert Driver-Tree (Neo4j), zieht Lineage (OpenMetadata), sucht korrelierte Anomalien.
- **Quant** — vergleicht Forecast-Diff, korreliert mit Driver-Knoten, rechnet Erklärungs-Anteile.
- **Reporter** — synthetisiert RCA-Hypothese mit Evidence-Snippets.

PII-Hit → Force-Local. Output → `insights` mit `severity`, `what_happened`, `why_hypothesis`, `evidence_id`.

**Forecasting (FR-05).** ARIMA/Prophet (statistisch) + GBT (driver-basiert) + Quantil-Regression + Monte-Carlo (10–100k Pfade). Models in MinIO `gold/models/<tenant>/`. GPU-Acceleration auf DGX.

### 2.3 Action-Tier

**Briefing-Generator (FR-07).** Daily/Weekly/Monthly. Sammelt Top-Mover, Anomalien, RCAs, Driver-Pfade, Benchmarks. Erzeugt Markdown → Docling → PDF, optional Documenso-Signatur. Distribution via n8n (Mail, Slack, Teams). Performance-Ziel: < 90s P95.

**Benchmark (FR-08).** Skill `kpi-market-intel` definiert Crawl-Pläne (Statista, Eurostat, Bundesbank, ECB, Branchen-Reports). Crawl4AI für öffentliche Inhalte, Nimble für SaaS-Aggregation. Lizenz-Metadaten Pflicht. Cache in `benchmarks` (ClickHouse).

**Action-Orchestrator (FR-09).** Wrapper um n8n. Maßnahmen-Templates: „Mahnlauf anstoßen", „Pricing-Review einberufen", „Lieferanten-Eskalation", „Marketing-Budget umschichten". Workflow: Vorschlag → Evidence → Approver → Pre-Snapshot → Execute → Post-Smoke → Audit. **Niemals auto-apply.**

### 2.4 Compliance-Tier

**Compliance-Auditor (FR-10).** Quartals-Cron. Mappt jeden Agent-Run und jede Maßnahme auf:
- EU AI Act Art. 26 (Deployer-Pflichten),
- Art. 27 (FRIA),
- ISO 27001 Annex A,
- GDPR Art. 30 + 35.

Erzeugt Compliance-Dossier (PDF) signiert via Documenso, ablegt in `evidence/compliance/<tenant>/<quarter>/`.

## 3. Modell-Routing (Hybrid-LLM-Default)

```
Request
  ↓
Presidio PII-Scan
  ↓
Skill-Manifest external = ?
  ↓
Datenklassifikation ∈ {public, anonymized}?
  ↓
Tenant-Policy external_llm_allowed?
  ↓
LiteLLM Virtual Key Quota?
  ↓
[lokal | extern]
  ↓
generative-shield Output-Filter
  ↓
Langfuse Trace + ClickHouse Audit
```

Lokal: `qwen3-72b-local` (default), `llama3-70b-local` (fallback), `qwen3-vl-multimodal` (Bilder/Charts).
Extern (policy-gated): `claude-opus-4-7` (komplexes Reasoning), `gpt-4-class via OpenRouter` (vergleichende Analyse).

Bei jedem Veto eines Gates: Block + Local-Fallback + Audit mit Reason.

## 4. Tool-Bindings (gemeinsame Toolings im Orchestrator)

| Tool-Name | Zweck | Bindings |
| --- | --- | --- |
| `trino.query` | Federated SQL | Trino HTTP |
| `clickhouse.query` | Hochfrequente Time-Series | CH HTTP |
| `postgres.query` | Metric-Definitions, OKRs | PG via app.tenant RLS |
| `neo4j.cypher` | Driver-Tree Traversal | Bolt + Tenant-Property-Filter |
| `opensearch.search` | BM25 + Logs | OS HTTP |
| `qdrant.search` | Vector Recall | Qdrant gRPC, Collection pro Tenant |
| `letta.recall` | Long-term Memory | Letta API |
| `docling.render` | Markdown → PDF | Docling Container |
| `documenso.sign` | Signatur | Documenso API |
| `presidio.scan` | PII-Detection | Presidio HTTP |
| `shield.filter` | Output-Filter | generative-shield HTTP |
| `crawl4ai.fetch` | Web-Crawl | Crawl4AI HTTP |
| `nimble.fetch` | SaaS-Aggregation | Nimble HTTP |
| `n8n.trigger` | Workflow-Apply | n8n Webhook |

Jeder Tool-Call schreibt in den Agent-Run-Trace (ClickHouse `agent_runs_<tenant>` + Langfuse).

## 5. Eval-Hooks

Jeder Agent hat in `kpi-evals` Skill und im rm-repo unter `evals/<agent>/` ein Set:

- **Goldene Traces** — referenz-Inputs + erwarteter Output-Schema + erwartete Tool-Call-Sequenz.
- **Replay-Tests** — deterministisch via Seed + Mocked LLM oder kontrolliertem lokalem Modell.
- **Akzeptanz-Schwellen** — z. B. KPI-Discovery: Recall ≥ 0.6 auf Test-Datasets, RCA: Top-3 Hypothese korrekt in ≥ 50 % der Fälle.
- **Regression-Gate** — neuer Skill-Stand muss mind. so gut sein wie aktueller, sonst CI-Block.

## 6. Failure-Modes & Fallbacks

| Failure | Auswirkung | Fallback |
| --- | --- | --- |
| LLM down (lokal) | Agents stalled | LiteLLM cycling auf `llama3-70b-local`, sonst Pause + Alert |
| LLM down (Cloud) | Externe Pfade stalled | Force-Local; bei Block-on-PII Briefing als „degraded" markieren |
| Trino down | Discovery + Briefing degraded | Cache aus ClickHouse für KPIs der letzten 24h, kein Discovery |
| Neo4j down | Driver-Tree-Read fail | Read-only-Modus aus PG-Mirror, kein Update |
| MinIO down | Evidence + Briefing-PDF fail | Evidence in PG-Backup-Tabelle queue, nachreichen |
| Presidio down | PII-Gate Open | **Hard fail** — keine LLM-Aufrufe, Alert |
| n8n down | Action-Apply fail | Approval-Freigabe wartet, Alarm an Admin |
| Langfuse down | Trace-Loss | ClickHouse-Audit reicht für Pflicht; Langfuse später nachladen |

## 7. Skill-Mapping

| Agent | Primär-Skill | Sekundär |
| --- | --- | --- |
| KPI-Discovery | `kpi-mining-product` | `kpi-metric-contracts`, `kpi-evals` |
| Data-Profiler | `kpi-mining-ops` | – |
| Semantic-Mapper | `kpi-mining-product` | `kpi-market-intel` |
| Anomaly-Detector | `kpi-agent-runtime` | – |
| RCA | `kpi-agent-runtime` | `kpi-evals` |
| Forecasting | `kpi-agent-runtime` | – |
| Briefing | `kpi-mining-product` | `kpi-agent-runtime` |
| Benchmark | `kpi-market-intel` | – |
| Action-Orchestrator | `kpi-mining-ops` | `kpi-tenant-onboarding` |
| Compliance | `kpi-mining-ops` | `kpi-evals` |
