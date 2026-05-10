{{
    config(
        materialized='table',
        contract={'enforced': true}
    )
}}
select
    as_of_month,
    sum(case when is_active then mrr_eur else 0 end)        as mrr_eur,
    count(distinct case when is_active then subscription_id end) as active_subscription_count
from {{ ref('stg_subscriptions') }}
group by 1
order by 1
