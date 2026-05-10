# dbt project — kpi_enterprise

Source-of-truth dbt project that produces the gold-layer marts which back
the metric contracts under `../metric-contracts/`.

## Layout

```
contracts/dbt/
├── dbt_project.yml
├── profiles.example.yml          # copy to ~/.dbt/profiles.yml
├── models/
│   ├── sources.yml               # raw bronze tables (Airbyte-landed)
│   ├── staging/                  # cleansing + type-casting (views)
│   │   ├── stg_subscriptions.sql
│   │   ├── stg_invoices.sql
│   │   ├── stg_opportunities.sql
│   │   ├── stg_orders.sql
│   │   └── stg_nps_responses.sql
│   └── marts/                    # gold-layer facts (tables, contract-enforced)
│       ├── schema.yml            # data contracts
│       ├── fct_mrr_monthly.sql           ← finance.mrr
│       ├── fct_revenue_monthly.sql       ← finance.revenue + finance.cogs
│       ├── fct_sales_cycle_weekly.sql    ← sales.cycle_days
│       ├── fct_order_backlog_daily.sql   ← ops.order_backlog
│       └── fct_nps_monthly.sql           ← support.nps
└── README.md
```

## Quick start

```bash
pip install dbt-postgres
cp contracts/dbt/profiles.example.yml ~/.dbt/profiles.yml
cd contracts/dbt
dbt deps                       # if a packages.yml is added later
dbt seed                       # if any seeds are added
dbt build --select staging     # cleansing
dbt build --select marts       # contract-enforced facts
dbt test                       # source freshness + uniqueness
```

## Contract enforcement

Marts have `contract: { enforced: true }` set both at the
`dbt_project.yml` level and per-model. Adding/removing a column or
changing a type fails the build. This guarantees that downstream
consumers (orchestrator, briefings, BI) see a stable schema.

## Tenant isolation

The dbt models are tenant-agnostic at compile time. Tenant-scoping is
applied at the warehouse layer:
- Trino catalog mapping `kpi.<tenant>` (read-only views).
- Postgres RLS (`SET app.tenant = '<id>'`).
- Production runs schedule one dbt invocation per tenant with
  `target=<tenant>` and a profiles override.

See `../../tenants/TENANT-ISOLATION-CONTRACT.md §2` for the full layer-map.

## Mapping to metric contracts

| dbt model                         | Metric contract                                     |
| --------------------------------- | --------------------------------------------------- |
| `marts.fct_mrr_monthly`           | `monthly_recurring_revenue`                         |
| `marts.fct_revenue_monthly`       | `revenue`, `cost_of_goods_sold`                     |
| `marts.fct_sales_cycle_weekly`    | `sales_cycle_days`                                  |
| `marts.fct_order_backlog_daily`   | `order_backlog_eur`                                 |
| `marts.fct_nps_monthly`           | `net_promoter_score`                                |
