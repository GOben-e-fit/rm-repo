with raw as (
    select * from {{ source('raw', 'opportunities') }}
)
select
    opportunity_id,
    stage,
    cast(created_at as timestamptz)  as created_at,
    cast(closed_at as timestamptz)   as closed_at,
    case when stage = 'closed_won' then true else false end as is_won,
    case
        when closed_at is null then null
        else extract(epoch from (closed_at - created_at)) / 86400.0
    end as cycle_days
from raw
