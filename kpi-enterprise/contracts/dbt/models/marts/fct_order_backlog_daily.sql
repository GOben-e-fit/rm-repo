{{
    config(
        materialized='table',
        contract={'enforced': true}
    )
}}
select
    current_date as as_of_date,
    sum(open_amount_eur) filter (where is_in_backlog) as backlog_eur,
    count(*)             filter (where is_in_backlog) as backlog_order_count
from {{ ref('stg_orders') }}
