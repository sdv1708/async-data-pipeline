with page_views as (
    select distinct user_id from {{ source('analytics', 'page_views') }}
),
signups as (
    select distinct user_id from {{ source('analytics', 'signups') }}
),
purchases as (
    select distinct user_id from {{ source('sales', 'orders') }}
)
select
    (select count(*) from page_views) as total_page_views,
    (select count(*) from signups) as total_signups,
    (select count(*) from purchases) as total_purchases
