{{ config(materialized='table') }}

-- Construction events within 100 m of each candidate route, with hours allocated by year.
-- An event is represented by its start point, its end point (if present), and points every
-- 50 m along the straight line between them when the event is 5 miles or shorter. Longer
-- events are matched on endpoints only and flagged (is_long_event), because the road between
-- two endpoints 50 miles apart is unknown. Grain: (event_id, path_name, year).

{% set m_per_deg_lat = 110574 %}
{% set m_per_deg_lng = 87900 %}   {# 111320 × cos(37.8°) #}

with bay_area_events as (

    select *
    from {{ ref('stg_construction') }}
    where event_type = 'construction'
      and start_lat between 37.2 and 38.3
      and start_lng between -122.8 and -121.7

),

event_points as (

    select
        e.event_id,
        e.start_lng + (coalesce(e.end_lng, e.start_lng) - e.start_lng) * s.frac as lng,
        e.start_lat + (coalesce(e.end_lat, e.start_lat) - e.start_lat) * s.frac as lat
    from bay_area_events e
    cross join lateral (
        select generate_series(0, n) / n::double precision as frac
        from (
            select case
                when e.end_lat is null or e.distance_mi > 5 then 1
                else greatest(1, ceil(
                    sqrt(
                        power((e.end_lng - e.start_lng) * {{ m_per_deg_lng }}, 2)
                      + power((e.end_lat - e.start_lat) * {{ m_per_deg_lat }}, 2)
                    ) / 50.0
                ))::int
            end as n
        ) t
    ) s

),

point_cells as (

    select
        event_id, lng, lat,
        floor(lng / 0.00115)::int as cell_x,
        floor(lat / 0.0009)::int  as cell_y
    from event_points

),

vertex_cells as (

    -- each vertex listed under its own cell and the 8 around it
    select v.path_name, v.lng, v.lat, v.cell_x + dx as cell_x, v.cell_y + dy as cell_y
    from {{ ref('stg_routes') }} v
    cross join generate_series(-1, 1) as dx
    cross join generate_series(-1, 1) as dy

),

candidate_pairs as (

    select
        p.event_id,
        v.path_name,
        sqrt(
            power((p.lng - v.lng) * {{ m_per_deg_lng }}, 2)
          + power((p.lat - v.lat) * {{ m_per_deg_lat }}, 2)
        ) as distance_m
    from point_cells p
    join vertex_cells v
      on v.cell_x = p.cell_x
     and v.cell_y = p.cell_y

),

matches as (

    select event_id, path_name, min(distance_m) as min_distance_m
    from candidate_pairs
    group by 1, 2
    having min(distance_m) <= 100

),

years as (

    select
        y                                   as year,
        make_timestamp(y,     1, 1, 0, 0, 0) as year_start,
        make_timestamp(y + 1, 1, 1, 0, 0, 0) as year_end
    from generate_series(2017, 2021) as y

)

select
    m.event_id,
    m.path_name,
    m.min_distance_m,
    e.distance_mi                 as event_length_mi,
    e.distance_mi > 5             as is_long_event,
    e.severity,
    y.year,
    extract(epoch from (
        least(e.end_time, y.year_end) - greatest(e.start_time, y.year_start)
    )) / 3600.0                   as hours_in_year
from matches m
join bay_area_events e using (event_id)
join years y
  on e.start_time < y.year_end
 and e.end_time   > y.year_start