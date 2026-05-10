# COMPETITIVE-ANALYSIS — KPI Enterprise Mining

**Stand:** 2026-05-10 · abgeleitet aus [`../ARCHITECTURE-v2.md`](../ARCHITECTURE-v2.md) (Teil 1, Teil 7)
**Owner:** Market Intel (kpi-market-intel Skill)

> Wettbewerbskarte und Differenzierungs-Argumente für Sales/Marketing/Product.
> Alle Aussagen sind Anbieter-Claims (markiert) oder verifizierte
> Marktbeobachtung. Pricing-Angaben sind Listenpreise oder G2/Vendr-Verhandlungs-
> Benchmarks; reale Deals weichen 20–40 % nach unten ab.

---

## 1. Markt-Snapshot 2026

Aus klassischer BI ist **Agentic Analytics** geworden. Jeder Big-Player hat jetzt:
- Semantic Layer (eigen oder via dbt/Cube),
- LLM-Agents für NL→SQL,
- proaktive Insight-Feeds,
- Anomalie-Erkennung,
- Driver-Trees (zumindest light),
- MCP-Anbindung.

Diese Bausteine sind **Tabellenstakes**. Differenziert wird auf vier Achsen:

1. **Souveränität & On-Prem** (EU AI Act August 2026, „Digital Omnibus" Diskussion)
2. **Echte Mandantenfähigkeit** (Daten + Index + Agent)
3. **Hybrid-LLM-Routing** mit Policy-Gates
4. **Audit-Trail & SelfCLAW-Governance**

## 2. Vergleichs-Cluster (Kurzform)

### Cluster A — CFO/CEO-Plattformen (direktester Vergleich)

**ValueWorks.ai** (Karlsruhe). Stärkstes DACH-Vergleichsobjekt. KPI-Tree, Liquiditätsplanung, Investor-Reporting, OKR + AI, Co-Pilot, statistisches + KI-Forecasting, ERP/CRM/HR-Connectoren. ~25–100 k €/Mandant/Jahr.
**Schwächen:** kein On-Prem, keine EU-AI-Act-Story, geschlossenes Ökosystem (kein dbt/OpenMetadata/Neo4j), Sprache primär EN.

**Drivetrain, Mosaic, Abacum** — modernes FP&A, SaaS-only.

### Cluster B — Agentic-BI-Incumbents

**ThoughtSpot Spotter / SpotterModel / SpotterViz / Spotter 3 / SpotterCode + MCP Server.** Spotter 3 (2025) blendet structured + unstructured. Pricing: Essentials $25/User/Mo, Pro $50/User/Mo oder ~$0.10/Query, Enterprise custom (G2: ab $12k/Mo, Großdeals > $500k/Jahr). LLM via GPT/Gemini/Cortex/Claude.
**Schwächen:** Pro-Plan kein echtes Multi-Tenant; AI-Features lt. Reviews „half-baked" bei komplexen Fragen; intransparent; kein On-Prem.

**Tableau Pulse + Tableau Agent + Agentforce.** Pulse in jeder Cloud-Edition; Enhanced Q&A nur in Tableau+ (Premium). Insight-Feeds, Slack/Email-Digests. AI über Einstein/Agentforce Trust Layer mit Azure OpenAI. Pricing: Creator ~$75, Explorer ~$42, Viewer ~$15/User/Mo.
**Schwächen:** harte Salesforce-Bias, kein On-Prem, Tableau+ AI nur mit Salesforce-Org, keine offene Agent-API.

**Qlik Discovery Agent + Qlik Answers + Qlik MCP Server.** Discovery Agent monitort Apps proaktiv auf statistisch signifikante Anomalien. Qlik Answers vereint structured + unstructured + Action-Trigger. Talend Cloud + AI Trust Score (Juli 2025) + Iceberg Open Lakehouse.
**Schwächen:** Vendor-Lock auf Qlik-Apps; Discovery Agent nur EN; keine fine-grained Access Control für Discovery Agent (lt. Qlik Help); klassische SaaS-Architektur.

**Microsoft Fabric + Copilot.** Seit April 2025 ab Capacity F2 (vorher F64). Abrechnung via CU-sec (400 in / 1.200 out pro 1k Token). FCC-Capacity. Fabric Data Agents für NL.
**Schwächen:** Datenresidenz EU/US-Boundary, Azure-only, kein DGX/On-Prem, Power-BI-Pro-Lizenz weiterhin nötig unter F64.

### Cluster C — Connected Planning / FP&A

**Anaplan** (Hyperblock + Polaris). Multidimensional, 18-Mo-Implementations üblich. $50–500k/Jahr.
**Pigment** — AI-native EPM, AI-Agents für „Mini-CFO". Vendr 20–40 % unter Anaplan im Mid-Market.
**Workday Adaptive Planning** — ab $50k/Jahr, sinnvoll mit Workday-HCM/Financial-Stack.

Alle Closed-Source-SaaS, kein DGX/On-Prem.

### Cluster D — Semantic Layer / Headless BI

**Cube (Cube Cloud + Cube D3).** GigaOm-Leader 2025, Gartner-Market-Guide for Agentic Analytics 2026. OSS Core 18k+ Stars, REST/GraphQL/SQL/MDX/DAX/AI-API. Wird zur infrastrukturellen Basis vieler Agentic-BI-Stacks.

> Gartner-Prognose Jan 2026 (Vorhersage, nicht beobachtet): „60 % der Agentic-Analytics-Projekte, die nur auf MCP setzen, werden bis 2028 wegen fehlendem Semantic Layer scheitern."

**AtScale, GoodData, dbt Semantic Layer (MetricFlow), Snowflake Semantic Views (GA Nov 2025), Databricks Metric Views.**

**Konsequenz für uns:** Wir bauen **keinen** eigenen Semantic Layer. Wir nutzen **dbt + dbt Data Contracts + Trino + OpenMetadata** als „logischen" Semantic Layer; Cube Core OSS bleibt als optionaler Aggregations-/AI-API-Layer reserviert.

### Cluster E — Data Catalogs / Lineage / Governance

**Atlan** — Gartner MQ Leader 2025 (Metadata) + 2026 (D&A Governance), Forrester Wave Leader 2024+2025. „Context Layer for AI" mit MCP-Server. SaaS-first.

**Collibra** — Enterprise-Governance, QueryFlow-Lineage, 3–9 Mo Deployment.

**OpenMetadata / Collate** — Open Source, Apache-Iceberg-basiertes Metadata-Lakehouse, column-level Lineage, GA-grade. **Strategischer Vorteil: läuft bereits auf catalog.medialine.app + meta.medialine.app.**

### Cluster F — Data Observability

**Monte Carlo** — Pionier, ML-Anomaly, Field-Level-Lineage, ~$100k+/Jahr. **Datafold** — Data-Diff vor Deployment, dbt-native. **Metaplane** — April 2025 von Datadog akquiriert. Beide ergänzen Data-Quality-Drift, das KPI Enterprise Mining mitbedienen muss.

### Cluster G — AI-Native Datawork-Tools (Komplementär)

**MotherDuck** (managed DuckDB), **Dust** (AI-Agent-Workspace), **Glean Work AI** (Enterprise-RAG-Search). Eher Komplementär als Wettbewerber.

### Cluster H — Agentic-BI-Startups

**Athenic AI** (SF, $4.3M Seed Jan 2025, BMW i Ventures lead) — Knowledge-Graph + LLM. **Quaeris** ($2.75M) — konversationelle BI / Enterprise Search. **Hyperbound, Delphi AI, Praxis AI, WisdomAI, Zenlytic, Seek AI, Domyn, Fluent (formerly Channel)** — alle Frühphase, $5–25M Funding, schmal, kein On-Prem.

## 3. Feature-Matrix Tabellenstakes vs. Differenzierer

| Feature | Tabellenstakes | Differenzierer | KPI Enterprise Mining v2 |
| --- | --- | --- | --- |
| KPI-Catalog | alle | – | + 100+ Templates |
| Driver-Tree | ValueWorks, Tableau Pulse, Pigment | – | Neo4j |
| NL→SQL | alle | – | LiteLLM + Trino |
| Anomaly Detection | Qlik, Pulse, ThoughtSpot, Monte Carlo | – | Discovery-äquivalent |
| Semantic Layer | Cube, dbt, Snowflake, Databricks | – | dbt + Contracts + Trino |
| Audit-Trail Agent-Runs | – | Differenzierer | Langfuse + ClickHouse |
| EU AI Act Art. 26/27 ready | – | starker Differenzierer | Compliance-Agent |
| Souveränität / On-Prem | nur Qlik teilweise | Killer-Differenzierer | DGX Spark |
| Multi-Tenant (Daten+Agent+Index) | nur ThoughtSpot Enterprise | Differenzierer | Keycloak Realms + RLS + Qdrant |
| Hybrid-LLM Policy | – | Differenzierer | LiteLLM + Presidio + Shield |
| HITL Action-Orchestrator | nur Pigment teilweise | Differenzierer | n8n + Documenso |
| Open-Source Stack | – | Differenzierer | dbt, Trino, OpenMetadata, Neo4j |
| Proaktiver Insight-Feed | Qlik, Pulse, Spotter | – | Briefing-Generator |

## 4. Pricing-Karte

| Modell | Beispiel | Range |
| --- | --- | --- |
| Per Seat | Tableau, ThoughtSpot Essentials | $15–75/User/Mo |
| Per Capacity | MS Fabric F2–F128 | ~€280/Mo (F2) bis €18k/Mo (F64) |
| Per Query / Usage | ThoughtSpot Pro $0.10/Query | nutzungsabhängig |
| Per Tenant Platform Fee | Pigment, Anaplan | $50–500k/Jahr |
| Per Mandant Mid-Market DACH | ValueWorks (geschätzt) | €25–100k/Jahr |

**Vorschlag KPI Enterprise Mining (siehe `PRODUCT-SPEC.md §8`):** Plattform €18–60k/Jahr (Tier S/M/L) + Per-Seat Add-on €25–75/User/Mo ab Seat 11 + DGX-Compute-Pauschale + Compliance-Pack +€6k/Jahr.

## 5. Marktlücke / Positionierungssatz

> „On-prem-souveränes, mandantenfähiges Agentic-KPI-System mit DGX-GPU-Power,
> EU-AI-Act-audit-ready, mit offenem dbt/Trino/OpenMetadata/Neo4j-Stack, das
> CFO/CEO/COO-Briefings, Driver-Trees, Maßnahmen-Workflows und externe Benchmarks
> in einem System liefert – ohne dass Daten den Mandanten-Perimeter verlassen."

Diese Position ist von Tableau/ThoughtSpot/Qlik/Fabric/Pigment/Anaplan/ValueWorks **strukturell nicht erreichbar** (Salesforce/Azure/AWS/Google-Lock). Atlan/Collibra/OpenMetadata sind nur Catalog. Athenic/Quaeris fehlen Mandantenfähigkeit + DGX.

## 6. TAM / SAM / SOM

- **TAM EU FP&A + augmented BI 2026:** ~$14–16 Mrd (Gartner/IDC-Mischschätzung).
- **Souveräner On-Prem-Anteil:** <5 % heute, prognostiziert 12–18 % bis 2028 (EU-AI-Act-Effekt).
- **Adressierbares Sub-TAM:** $700M – $2.5 Mrd.
- **SAM** (DACH-regulierter Mittelstand + PE): $120–250M.
- **SOM v1 (3 Jahre)** bei 1–2 % Penetration: **€8–25M ARR**.

## 7. Win/Loss-Argumente (Sales-Cheat-Sheet)

**Wir gewinnen, wenn:**
- Kunde DGX-Souveränität/EU-AI-Act zwingend braucht.
- Multi-Tenant für PE-Portfolios oder Implementation-Partner gefragt ist.
- Open-Source-Stack-Compatibility (dbt/Trino/OpenMetadata/Neo4j) Pflicht ist.
- HITL-Approval + Audit-Trail explizit ausgeschrieben sind.

**Wir verlieren, wenn:**
- Kunde alles-bei-Salesforce/Azure-only-Lock akzeptiert.
- Kunde nur „Dashboard mit AI-Chat" sucht und keinen Driver-Tree/RCA braucht.
- Kunde fertige Branchen-KPI-Bibliothek mit 200+ vordefinierten KPIs vom Standard-SaaS-Anbieter erwartet (gegen ValueWorks im 0-Tag-Onboarding-Vergleich).

**Gegenmaßnahmen Lost-Case 3:**
- 100+ Branchen-Templates aus `kpi-mining-product` Skill als Quickstart-Library.
- Onboarding-Wizard mit Industry-Picker + automatischer Default-Discovery.

## 8. Quellen-Liste (zu vervollständigen)

> Roh-Input wurde nach „Monte Carlo / Datafold / M..." abgeschnitten. Vollständige
> URL-Liste wird beim nächsten Crawl-Run von `kpi-market-intel` Skill gegen
> rebuild und hier ergänzt.

**Wettbewerber (Kurzliste):**
- ValueWorks: `valueworks.ai/product/`, `/use-cases-planning-forecasting/`, `/platform-capabilities/`, `/customers/`, `/journey-of-sme-cfos/`
- ThoughtSpot: `thoughtspot.com/pricing`, `thoughtspot.com/product/spotter`
- Tableau: `tableau.com/products/pulse`, `salesforce.com/agentforce`
- Qlik: Qlik Connect 2025 Press, Discovery Agent Product Page, Qlik Help
- Pigment: `pigment.com/platform`, `vendr.com/marketplace/pigment`
- Anaplan/Workday: ViewpointAnalysis FP&A 2026
- Cube: `cube.dev`, GitHub `cube-js/cube`, GigaOm Radar 2025
- Athenic/Quaeris: BMW i Ventures Press Jan 2025, TechCrunch, PitchBook, CB Insights
- Atlan/Collibra/OpenMetadata: `atlan.com`, ovaledge.com „12 Open Source AI Lineage Tools"

**Reports / Standards:**
- Gartner MQ Metadata Management 2025
- Gartner Market Guide for Agentic Analytics 2026
- Forrester Wave Data Governance Q3 2025
- GigaOm Radar Semantic Layers 2025
- EU AI Act – Verordnung (EU) 2024/1689, insb. Art. 9–17, 26, 27 (Stichtag 2026-08-02)
- ISO/IEC 27001:2022 Annex A
- DSGVO Art. 30, Art. 35
- HGB §257
