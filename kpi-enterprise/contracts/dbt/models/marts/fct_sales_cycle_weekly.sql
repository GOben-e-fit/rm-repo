{{
    config(
        materialized='table',
        contract={'enforced': true}
    )
}}
select
    date_trunc('week', closed_at) as week_start,
    avg(cycle_days)               as avg_cycle_days,
    count(*) filter (where is_won) as won_opportunities,
    count(*)                      as closed_opportunities
from {{ ref('stg_opportunities') }}
where closed_at is not null
group by 1
order by 1
