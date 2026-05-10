---
name: kpi-metric-contracts
description: Use for KPI metric definitions, formulas, grains, data contracts, golden datasets, reconciliation tests, lineage, OpenMetadata, dbt and metric-store validation.
---

# KPI Metric Contracts

Use this skill when creating or validating KPI definitions, formulas, contracts,
source lineage, reconciliation checks or metric-store APIs.

## Required Metric Fields

- `metric_id`
- `name`
- `owner`
- `formula`
- `grain`
- `dimensions`
- `source_systems`
- `data_class`
- `tenant_scope`
- `lineage_refs`
- `reconciliation_tests`
- `evidence_policy`

## Validation Pattern

1. Define formula and business meaning in plain language.
2. Specify grain and dimensions before implementing aggregation.
3. Map every input to source systems and lineage references.
4. Add golden dataset fixtures for expected output.
5. Add reconciliation tests against raw/GL/source facts.
6. Mark sensitivity and model-routing policy.
7. Require evidence artifacts for executive-facing insights.

## Guardrails

- Do not ship executive KPIs as ad hoc SQL without owner, formula version and reconciliation state.
- Use structured parsers or dbt/Data Contract tooling when available.
- Cross-tenant test fixtures are required for metrics that query shared stores.
