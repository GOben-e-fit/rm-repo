with raw as (
    select * from {{ source('raw', 'orders') }}
)
select
    order_id,
    status,
    cast(open_amount as numeric(18,2)) as open_amount_eur,
    case when status in ('confirmed','in_production','awaiting_shipment') then true else false end as is_in_backlog
from raw
