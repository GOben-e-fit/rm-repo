{{
    config(
        materialized='table',
        contract={'enforced': true}
    )
}}
select
    invoice_month,
    sum(revenue_eur)                                            as revenue_eur,
    sum(cogs_eur)                                               as cogs_eur,
    sum(revenue_eur) - sum(cogs_eur)                            as gross_margin_eur,
    case when sum(revenue_eur) > 0
         then (sum(revenue_eur) - sum(cogs_eur)) / sum(revenue_eur)
         else null
    end                                                          as gross_margin_pct
from {{ ref('stg_invoices') }}
group by 1
order by 1
