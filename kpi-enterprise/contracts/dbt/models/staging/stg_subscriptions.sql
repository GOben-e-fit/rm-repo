with raw as (
    select * from {{ source('raw', 'subscriptions') }}
)
select
    subscription_id,
    customer_id,
    cast(mrr_eur as numeric(18,2))      as mrr_eur,
    coalesce(active, false)             as is_active,
    date_trunc('month', as_of_month)    as as_of_month
from raw
