-- Q2: New York (five boroughs) by start year — what carried the 2021 step.
-- pct_over_30_days: events lasting 720+ hours; these carry the hours.
select
    extract(year from start_time)::int                                              as year,
    count(*)                                                                        as events,
    round(avg(duration_hours))                                                      as mean_hours,
    round(100.0 * count(*) filter (where duration_hours < 1) / count(*), 1)         as pct_sub_hour,
    round(100.0 * count(*) filter (where duration_hours >= 720) / count(*), 1)      as pct_over_30_days,
    count(*) filter (where duration_hours >= 720)                                    as events_over_30_days
from analytics.stg_construction
where event_type = 'construction'
  and city_normalized = 'New York' and state = 'NY'
group by 1
order by 1;
