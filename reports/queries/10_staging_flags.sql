-- Staging: how many rows each flag touches, by event type.
select
    event_type,
    count(*)                                                     as events,
    count(*) filter (where is_open_at_extract)                   as open_at_extract,
    count(*) filter (where is_batch_start)                       as batch_start,
    count(*) filter (where is_batch_end)                         as batch_end,
    count(*) filter (where end_time < start_time)                as negative_duration,
    round(avg(duration_hours))                                   as mean_hours,
    round((percentile_cont(0.5) within group (order by duration_hours))::numeric, 1) as median_hours
from analytics.stg_construction
group by 1
order by 1;
