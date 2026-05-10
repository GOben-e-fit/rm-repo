# PRODUCT-SPEC — KPI Enterprise Mining

**Stand:** 2026-05-10 · abgeleitet aus [`ARCHITECTURE-v2.md`](ARCHITECTURE-v2.md) (Teil 0, 1.4, 1.5, 2.1, 2.2, 5)
**Owner:** Product (kpi-mining-product Skill)

> Dieses Dokument fasst die produkt- und anforderungsseitige Sicht für Stakeholder
> ohne Architektur-Tiefe zusammen. Quelle der Wahrheit bleibt `ARCHITECTURE-v2.md`.
> Inkonsistenzen → ARCHITECTURE-v2.md gewinnt, Spec wird angeglichen.

---

## 1. Produktversprechen (One-Liner)

> „On-prem-souveränes, mandantenfähiges Agentic-KPI-System mit DGX-GPU-Power,
> EU-AI-Act-audit-ready, das CFO/CEO/COO-Briefings, Driver-Trees,
> Maßnahmen-Workflows und externe Benchmarks in einem System liefert –
> ohne dass Daten den Mandanten-Perimeter verlassen."

## 2. Fünf Kern-Werte

1. **KPI-Discovery & Metric Contracts** — Quellen werden gescannt, Kandidaten-KPIs vorgeschlagen, jede Definition ist ein versionierter Vertrag.
2. **Driver-Tree & OKR-Lineage** — KPIs hängen in Wirkungsbäumen (Neo4j) und sind mit OKRs/Maßnahmen verknüpft.
3. **C-Level-Briefing + Benchmark-Agent** — daily/weekly/monthly „Was/Warum/Was tun" inkl. Marktvergleich.
4. **Action-Orchestrator mit HITL** — Maßnahmen laufen über n8n/Slack/Teams/Documenso, niemals auto-apply.
5. **Compliance-/Audit-Agent** — EU AI Act Art. 26+27, ISO 27001, GDPR, durchgängige Trace-Spur.

## 3. Buyer Personas (Priorisiert)

| Persona | Pain | Was sie kaufen |
| --- | --- | --- |
| CFO Mittelstand (50–500 Mio €) | Excel-Wildwuchs, kein einheitliches KPI-Dictionary, manuelles Investor-Reporting | Investor-Pack + Liquiditätsplanung + KPI-Briefings |
| CEO/COO Holding/PE-Portfolio | Konsolidierte Sicht über 5–30 Beteiligungen fehlt | Multi-Tenant-Konsolidierung + Benchmark + „Was tun" |
| Group Controller / FP&A Lead | Anaplan-Komplexität ohne Mehrwert | dbt-/Git-Workflow + Driver-Trees + Forecasts |
| CIO/CISO regulierte Branche | Souveränität non-negotiable, EU-AI-Act-Druck | On-Prem + Compliance-Dossier + Audit-Trail |
| medialine/ki-guru als Implementation-Partner | will Multi-Tenant-Plattform statt pro-Kunde-Deploy | White-Label + Tenant-Onboarding-Wizard |

## 4. Markt-Positionierung (Kurzfassung)

Wir gewinnen nicht durch *mehr Features*, sondern durch **vier strukturelle Differenzierer**:

1. Souveränität & On-Prem (DGX Spark, kein Hyperscaler-Lock-in).
2. Mandantenfähigkeit auf Daten-/Index-/Agent-Ebene mit Deny-Tests als Release-Gate.
3. Hybrid-LLM-Routing (lokal default, Cloud nur policy-gated).
4. SelfCLAW-Governance (Evidence + Approval + Rollback + Audit).

Tabellenstakes (KPI-Catalog, Driver-Tree, NL-to-SQL, Anomaly Detection, Semantic Layer, proaktive Insights) liefern wir als Pflichtprogramm — siehe `ARCHITECTURE-v2.md §1.3`.

Strukturell **nicht erreichbare** Positionierung für: Tableau (Salesforce-Bias), ThoughtSpot (kein On-Prem), Qlik (Vendor-Lock), Microsoft Fabric (Azure-only), Pigment/Anaplan (SaaS-only), ValueWorks (kein On-Prem, geschlossen). Atlan/Collibra/OpenMetadata sind Catalog-Layer ohne KPI-Mining-Produkt. Athenic/Quaeris fehlen Mandantenfähigkeit + DGX.

## 5. Funktionale Anforderungen — Übersicht

| ID | Feature | Akzeptanz-Kurzform |
| --- | --- | --- |
| FR-01 | KPI-Discovery Agent | ≥ 25 Kandidaten in 30 Min, ≥ 60 % Review-Akzeptanz |
| FR-02 | Metric Contracts (versioniert, dbt+YAML+Postgres) | JSON-Schema-validiert, jede Observation referenziert Vertrags-Version |
| FR-03 | Driver-Tree Builder (Canvas + Neo4j) | Tree mit ≥ 30 Knoten lädt < 1,5 s |
| FR-04 | OKR-Lineage | KPI ↔ Objective ↔ Key-Result ↔ Maßnahme |
| FR-05 | Forecasting + Monte-Carlo | ARIMA/Prophet/GBT/Quantil + 10–100k Pfade |
| FR-06 | Anomaly + RCA Agent | STL/RobustZ/Prophet/IsoForest + CrewAI Researcher/Quant/Reporter |
| FR-07 | C-Level Briefing | Daily/Weekly/Monthly mit Was/Warum/Was tun/Benchmark, Mail+Slack/Teams |
| FR-08 | Benchmark-Agent | Crawl4AI/Nimble/Statista/Eurostat/Bundesbank, mit Lizenz-Metadaten |
| FR-09 | Action-Orchestrator HITL | n8n-Templates, Approval-Flow, Rollback-Snapshot, niemals auto |
| FR-10 | Compliance-Agent | EU-AI-Act Art. 26/27, ISO 27001, GDPR, Quartals-Dossier |
| FR-11 | Multi-Source Connectors | Airbyte/Upload/REST/Crawl4AI/Nimble |
| FR-12 | Tenant-Onboarding-Wizard | Time-to-First-Briefing ≤ 4 h |
| FR-13 | Hybrid-LLM-Routing | Presidio + generative-shield + LiteLLM Virtual Key |

Vollständige Texte: `ARCHITECTURE-v2.md §2.1`.

## 6. Nicht-funktionale Anforderungen — Schnell-Check

- **NFR-01** Tenant-Isolation in Postgres (RLS), Trino, MinIO, ClickHouse, Qdrant, OpenSearch, Neo4j, Agent-Runtime, LiteLLM. Cross-Tenant-Deny-Test ist **release-blocking**.
- **NFR-02** Audit über Langfuse + ClickHouse `agent_runs_<tenant>`, 7y Retention.
- **NFR-03** Default no-egress; externer LLM/API nur mit `external = true` im Vertrag.
- **NFR-04** Cockpit < 2 s P95, Driver-Tree < 1,5 s P95, Briefing < 90 s P95.
- **NFR-05** SelfCLAW: Snapshot + Evidence + Rollback bei jedem Apply.
- **NFR-06** ≥ 50 Mid-Tier-Tenants pro DGX-Box, horizontal über Tailscale-Overlay.
- **NFR-07** Keycloak Realm pro Tenant, JWT mit `tenant_id`-Pflichtclaim, sops+age.
- **NFR-08** Grafana/Loki/Tempo/Uptime Kuma/Prometheus + cost-proxy pro Tenant.

## 7. UX-Leitplanken (Cockpit)

Startscreen ist ein **Arbeitscockpit**, kein Dashboard. Die zwingenden fünf Spalten:

1. **Was ist passiert?** — Anomalien, Top-Mover (last 24h/7d/30d).
2. **Warum?** — RCA-Hypothese mit Evidence-Snippets.
3. **Was tun?** — 3–5 Maßnahmen mit erwartetem Impact.
4. **Wer ist Owner?** — Person, Rolle, Eskalationspfad.
5. **Welche Evidenz?** — Direktlinks ins Audit-Bundle / Langfuse-Trace.

Sekundär-Navigation: KPI-Katalog, Driver-Tree-Canvas, Datenquellen-Onboarding, Agent-Runs, Audit/Evidence, Admin/Tenant-Policy.

Brand-Switch über `data-brand` (ben-e-fit / ki-guru / medialine) zur Laufzeit, kein Build pro Tenant.

## 8. Pricing-Vorschlag (nicht final)

- Plattform-Lizenz pro Mandant: **18–60 k €/Jahr** (Tier S/M/L) — N Connector-Slots, M Briefings/Monat, K Driver Trees inklusive.
- Per-Seat Add-on: **25–75 €/User/Monat** ab Seat 11.
- DGX-Compute-Pauschale (Fair-Use Tokens) mit Burst-Verrechnung über cost-proxy.
- Compliance-Pack (EU AI Act Bundle): **+6 k €/Jahr**.

Benchmark-Vergleich siehe `ARCHITECTURE-v2.md §1.6`.

## 9. Roadmap-Schnellblick

- **v1 (W1–W4) Cockpit-Stabilisierung** — Skelett deploy-fähig, 2 Test-Tenants, Deny-Tests grün, kpi.ben-e-fit.ai mit Login.
- **v2 (W5–W9) Echte Datenquellen + KPI-Mining** — 1 Pilot zeigt 25+ echte KPIs, Driver-Tree ≥ 30 Knoten, mind. 1 Anomalie/Woche.
- **v3 (W10–W13) Autonome Agenten + HITL** — täglicher CFO-Briefing live, mind. 1 HITL-Maßnahme abgewickelt, Compliance-Dossier Q2/2026.

Detail-Gantt + Aufwand siehe `ARCHITECTURE-v2.md §5/§6`.

## 10. Offene Produktentscheidungen (an User)

1. **Pilot-Tenant für v1**: medialine intern, AlvI/R&M, oder ben-e-fit?
2. **Pricing-Modell**: Pro-Tenant-Flat, Pro-User, Pro-Metric-Volume, Hybrid mit Setup-Fee?
3. **Datenschutz-Default extern**: deny-all (nur lokal) vs. per-Tenant-Opt-in für anonymisierte Pfade?
4. **Wartungsfenster CP-099-Apply**: vor oder nach Akte-13 Phase-0-Pilot?
5. **Branding-Hierarchie**: ben-e-fit Hauptmarke, ki-guru Sister, medialine als Operator/Showcase — bestätigen oder umsortieren?
