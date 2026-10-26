{{ config(materialized='table') }}

-- Q4: construction exposure per candidate route, by year and for 2017–2021 combined.
-- Hours per route-mile is the headline; events per mile and severity-weighted hours per
-- mile alongside. Grain: (path_name, year), with year = 'all' for the five-year total.

with matched as (

    select * from {{ ref('int_route_events') }}

),

by_year as (

    select
        path_name,
        year::text                                               as year,
        count(distinct event_id)                                 as events,
        sum(hours_in_year)                                       as hours,
        sum(hours_in_year * severity)                            as severity_weighted_hours,
        count(distinct event_id) filter (where is_long_event)    as long_events
    from matched
    group by 1, 2

),

all_years as (

    select
        path_name,
        'all'                                                    as year,
        count(distinct event_id),
        sum(hours_in_year),
        sum(hours_in_year * severity),
        count(distinct event_id) filter (where is_long_event)
    from matched
    group by 1

),

combined as (

    select * from by_year
    union all
    select * from all_years

)

select
    r.path_name,
    r.distance_mi,
    c.year,
    coalesce(c.events, 0)                                                   as events,
    round(coalesce(c.hours, 0))                                             as hours,
    round(coalesce(c.hours, 0) / r.distance_mi)                             as hours_per_mile,
    round((coalesce(c.events, 0) / r.distance_mi)::numeric, 1)              as events_per_mile,
    round(coalesce(c.severity_weighted_hours, 0) / r.distance_mi)           as severity_weighted_hours_per_mile,
    coalesce(c.long_events, 0)                                              as long_events,
    rank() over (partition by c.year
                 order by coalesce(c.hours, 0) / r.distance_mi desc)        as rank_hours_per_mile
from {{ ref('sf_paths') }} r
left join combined c
  on c.path_name = r.path_name
order by c.year, rank_hours_per_mile