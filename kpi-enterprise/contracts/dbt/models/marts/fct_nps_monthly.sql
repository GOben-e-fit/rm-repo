{{
    config(
        materialized='table',
        contract={'enforced': true}
    )
}}
with monthly as (
    select
        date_trunc('month', submitted_at) as month_start,
        sum(case when nps_bucket = 'promoter'  then 1 else 0 end) as promoters,
        sum(case when nps_bucket = 'detractor' then 1 else 0 end) as detractors,
        count(*) as responses
    from {{ ref('stg_nps_responses') }}
    group by 1
)
select
    month_start,
    promoters,
    detractors,
    responses,
    case when responses > 0
         then 100.0 * (promoters - detractors)::float / responses
         else null
    end as nps_score
from monthly
order by 1
