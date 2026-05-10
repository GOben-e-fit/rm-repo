---
name: kpi-evals
description: Use for KPI Enterprise Mining route tests, data contract tests, tenant isolation tests, agent replay evals, RCA accuracy checks, hallucination/citation evals and ops release gates.
---

# KPI Evals

Use this skill when designing, running or reviewing tests for KPI Enterprise Mining.

## Eval Groups

- Route tests: domains, `/`, `/enterprise/`, `/api/health`, `/openapi.json`, cache-bust and screenshots.
- Data tests: golden KPI formulas, reconciliation, dbt/data-contract checks, lineage readback, ClickHouse readback.
- Tenant tests: RBAC, cross-tenant deny fixtures, row/source-level access, separate evidence artifacts, external-model deny for sensitive data.
- Agent tests: replay, prompt/version trace, citation checks, RCA accuracy, Monte-Carlo determinism, HITL approve/reject.
- Ops tests: backup/restore, audit completeness, rate limits, model fallback, async job load.

## Release Gate

Do not call the product release-ready unless:

- all critical route tests pass,
- metric contracts have golden fixtures,
- negative tenant tests pass,
- agent outputs are replayable and evidence-linked,
- rollback and evidence bundle are documented.
