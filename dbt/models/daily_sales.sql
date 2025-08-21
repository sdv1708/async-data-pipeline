select
    order_date::date as order_date,
    sum(amount) as total_sales
from {{ source('sales', 'orders') }}
group by 1
order by 1
