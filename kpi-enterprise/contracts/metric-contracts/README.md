# metric-contracts

Versioned, tenant-scoped definitions of every KPI in the system.
Each contract is a YAML file under
`contracts/metric-contracts/<tenant>/<metric>.yaml` and is enforced by
`schema.json` (release-blocking CI gate).

## Layout

```
contracts/metric-contracts/
├── schema.json        # JSON-Schema 2020-12 contract
├── validate.py        # CI-runnable validator (jsonschema + pyyaml)
├── README.md          # this file
└── example/           # canonical reference contracts
    ├── monthly_recurring_revenue.yaml
    ├── cash_runway_months.yaml
    ├── net_promoter_score.yaml
    ├── sales_cycle_days.yaml
    └── order_backlog_eur.yaml
```

Tenant-specific contracts go under `<tenant>/` (e.g.
`tnt_benefit/customer_acquisition_cost.yaml`). The `example/` folder is
seed material — copy + adapt when onboarding a real tenant.

## Validate locally

```bash
pip install jsonschema pyyaml
python contracts/metric-contracts/validate.py
```

CI: `.github/workflows/metric-contracts-validate.yml` runs on every
push touching this folder.

## Mandatory fields

`name`, `display_name`, `owner`, `domain`, `unit`, `granularity`,
`direction`, `expression`, `data_classification`. See `schema.json`
for full constraints.

## Cross-cutting rules (enforced by validator beyond schema)

- `external_llm_allowed: true` is rejected when
  `data_classification ∈ {confidential, pii}`. Hard rule from
  `../../tenants/TENANT-ISOLATION-CONTRACT.md §5`.

## Promotion path

```
PR with new/changed contract YAML
  → CI validates schema (this folder)
  → CI runs orchestrator pytest
  → Approver merges
  → Promote endpoint creates the metric_definitions row in the tenant's
    Postgres schema with version=1 (or +1 if already exists)
  → Observations start landing per refresh_cron
```
