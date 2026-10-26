-- Q2: what changed in the source, by start year (construction events only, deduplicated).
-- pct_96h: events with a duration of exactly 96 hours, a provider template.
-- pct_sub_hour: events under one hour — "Slow traffic ... due to roadwork" observations.
select
    extract(year from start_time)::int                                              as year,
    count(*)                                                                        as events,
    round(avg(duration_hours))                                                      as mean_hours,
    round((percentile_cont(0.5) within group (order by duration_hours))::numeric, 1) as median_hours,
    round(100.0 * count(*) filter (where round(duration_hours::numeric, 1) = 96) / count(*), 1) as pct_96h,
    round(100.0 * count(*) filter (where duration_hours < 1) / count(*), 1)                     as pct_sub_hour,
    round(100.0 * count(*) filter (where is_batch_start or is_batch_end) / count(*), 1)          as pct_batch
from analytics.stg_construction
where event_type = 'construction'
group by 1
order by 1;
