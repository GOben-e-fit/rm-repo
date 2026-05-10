with raw as (
    select * from {{ source('raw', 'nps_responses') }}
)
select
    response_id,
    cast(nps_score as int) as nps_score,
    cast(submitted_at as timestamptz) as submitted_at,
    case
        when nps_score >= 9 then 'promoter'
        when nps_score <= 6 then 'detractor'
        else 'passive'
    end as nps_bucket
from raw
where nps_score between 0 and 10
