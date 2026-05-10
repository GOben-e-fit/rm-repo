with raw as (
    select * from {{ source('raw', 'invoices') }}
)
select
    invoice_id,
    customer_id,
    cast(total_amount as numeric(18,2)) as revenue_eur,
    cast(cost_amount  as numeric(18,2)) as cogs_eur,
    cast(created_at   as timestamptz)   as invoiced_at,
    date_trunc('month', created_at)     as invoice_month
from raw
