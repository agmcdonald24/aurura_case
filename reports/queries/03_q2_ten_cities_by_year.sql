-- Q2: the ten cities with the most hours (Q1's list) by year. Hours are month-allocated,
-- so a multi-year event contributes to each year it was active.
with top_ten as (
    select city, state
    from analytics.int_city_month_hours
    group by 1, 2
    order by sum(construction_hours) desc nulls last
    limit 10
)
select
    m.city,
    m.state,
    extract(year from m.month)::int                       as year,
    sum(m.construction_events)                            as events,
    round(sum(m.construction_hours))                      as hours
from analytics.int_city_month_hours m
join top_ten t on t.city = m.city and t.state = m.state
group by 1, 2, 3
order by 1, 3;
