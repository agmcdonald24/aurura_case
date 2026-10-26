-- Q1: construction hours by city, 2017–2021, every city in the data, top ten.
-- Hours are allocated to the months each event overlaps (int_city_month_hours).
select
    city,
    state,
    sum(construction_events)                              as events,
    round(sum(construction_hours))                        as hours,
    round(sum(construction_hours_excl_batch))             as hours_excl_batch,
    round(sum(construction_hours) / (5 * 8760))           as avg_concurrent
from analytics.int_city_month_hours
group by 1, 2
order by hours desc nulls last
limit 10;
