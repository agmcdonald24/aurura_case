-- The most common event durations. Round values are provider templates; sub-hour
-- values are congestion observations.
select
    round(duration_hours::numeric, 1)                            as hours,
    count(*)                                                     as events,
    round(100.0 * count(*) / sum(count(*)) over (), 1)           as pct
from analytics.stg_construction
group by 1
order by 2 desc
limit 12;
