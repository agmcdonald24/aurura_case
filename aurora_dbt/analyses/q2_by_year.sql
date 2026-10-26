-- what changed by year: volume, duration, templates
select extract(year from start_time)::int                           as year,
       count(*)                                                      as events,
       round(avg(duration_hours))                                    as mean_hours,
       percentile_cont(0.5) within group (order by duration_hours)   as median_hours,
       round(100.0 * count(*) filter (where round(duration_hours::numeric, 1) = 96) / count(*), 1) as pct_96h,
       round(100.0 * count(*) filter (where duration_hours < 1) / count(*), 1)                     as pct_sub_hour,
       round(100.0 * count(*) filter (where is_batch_start or is_batch_end) / count(*), 1)          as pct_batch
from analytics.stg_construction
where event_type = 'construction'
group by 1
order by 1;