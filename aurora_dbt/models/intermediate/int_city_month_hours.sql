{{ config(materialized='table') }}

-- Construction hours per city per month, 2017–2021.
-- Each event's duration is allocated to the calendar months it overlaps, so long-running
-- and still-open events contribute hours to the months the work was actually happening.
-- Grain: (city, state, month). State is part of the grain because city names repeat
-- across states (Portland, Springfield, ...).

with months as (

    select
        month_start,
        month_start + interval '1 month' as month_end
    from generate_series(
        '2017-01-01'::timestamp,
        '2021-12-01'::timestamp,
        interval '1 month'
    ) as month_start

),

events as (

    select *
    from {{ ref('stg_construction') }}
    where end_time >= start_time        -- none in this extract; kept as documentation

),

event_months as (

    -- one row per (event, month) the event overlaps
    select
        e.event_id,
        e.city_normalized,
        e.state,
        e.event_type,
        e.is_batch_start,
        e.is_batch_end,
        m.month_start,
        extract(epoch from (
            least(e.end_time, m.month_end) - greatest(e.start_time, m.month_start)
        )) / 3600.0 as hours_in_month
    from events e
    join months m
      on e.start_time < m.month_end
     and e.end_time   > m.month_start

)

select
    city_normalized                                             as city,
    state,
    month_start                                                 as month,

    count(distinct event_id) filter (where event_type = 'construction')
                                                                as construction_events,
    sum(hours_in_month)      filter (where event_type = 'construction')
                                                                as construction_hours,
    sum(hours_in_month)      filter (where event_type = 'construction'
                                       and not is_batch_start
                                       and not is_batch_end)    as construction_hours_excl_batch,
    sum(hours_in_month)      filter (where event_type = 'seasonal_closure')
                                                                as seasonal_closure_hours

from event_months
group by 1, 2, 3