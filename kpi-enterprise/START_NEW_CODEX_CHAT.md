# Start: Akte 14 — KPI Enterprise Mining

Bitte für jeden neuen Codex- oder Claude-Code-Chat zu KPI Enterprise
Mining diesen Block am Anfang einfügen, damit Kontext sauber lädt.

---

## Boot

1. Lies `G:\Meine Ablage\codex\CODEX_TO_CLAUDE_HANDOVER.md`.
2. Aktiviere `rm-ki-plattform` Skill — beachte F-001..F-010.
3. Aktiviere die KPI-Skill-Familie:
   - `kpi-mining-product`
   - `kpi-mining-ops`
   - `kpi-metric-contracts`
   - `kpi-agent-runtime`
   - `kpi-market-intel`
   - `kpi-tenant-onboarding`
   - `kpi-evals`
4. Lies in dieser Reihenfolge:
   - `14-kpi-enterprise-mining/README.md`
   - `14-kpi-enterprise-mining/PRODUCT-SPEC.md`
   - `14-kpi-enterprise-mining/ARCHITECTURE.md`
   - `14-kpi-enterprise-mining/agents/AGENT-TOPOLOGY.md`
   - `14-kpi-enterprise-mining/tenants/TENANT-ISOLATION-CONTRACT.md`
   - `14-kpi-enterprise-mining/runbooks/CP-099-kpi-mining-governance-package.md`
5. Bei Routing-Fragen: `08-dgx-cloudflare-routing/`.
6. Bei Container-/Compose-Fragen: `09-dgx-core-platform/`.
7. Bei LiteLLM/Langfuse/Keycloak-Fragen:
   `10-dgx-litellm-langfuse-keycloak/`.
8. Bei Tenant-Onboarding: `11-ben-e-fit-ki-guru-tenants/` +
   `tenants/TENANT-ISOLATION-CONTRACT.md`.

## Harte Regeln

- Keine Live-Mutation an `kpi-mining`-Container, Tunnel, DNS,
  LiteLLM-Policies oder Volumes ohne CP-Slice.
- Keine Secret-Werte in Antworten oder Dateien — nur Pfade/Key-Namen.
- Keine Cross-Vermischung mit anderen Akten in einer Antwort.
- Hostname vor jedem Live-Apply prüfen (Soll: `spark-dev-01`).

## Aktueller Status

- v1: Spezifikation komplett, Apply offen via CP-099.
- v2: Spezifikation skizziert, geplant CP-104+.
- v3: Spezifikation skizziert, geplant CP-110+.
