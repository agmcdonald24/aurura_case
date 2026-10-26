{{ config(materialized='table') }}

-- Q3: the ten largest US cities, construction 2017–2021, normalized two ways.
-- Hours per square mile is the primary metric (closest available proxy for exposure per
-- road mile); hours per 100k residents is shown alongside because the city list itself is
-- a population ranking. Grain: one row per city.

with totals as (

    select
        city,
        state,
        sum(construction_events)              as events,
        sum(construction_hours)               as hours,
        sum(construction_hours_excl_batch)    as hours_excl_batch
    from {{ ref('int_city_month_hours') }}
    group by 1, 2

)

select
    r.city,
    r.state,
    r.population_2020,
    r.land_area_sq_mi,
    t.events,
    t.hours,
    t.hours_excl_batch,
    t.hours / (5 * 8760)                              as avg_concurrent_advisories,
    t.hours / r.land_area_sq_mi                       as hours_per_sq_mi,
    t.hours / (r.population_2020 / 100000.0)          as hours_per_100k_residents,
    t.events / r.land_area_sq_mi                      as events_per_sq_mi,
    rank() over (order by t.hours desc)               as rank_raw_hours,
    rank() over (order by t.hours / r.land_area_sq_mi desc)           as rank_per_sq_mi,
    rank() over (order by t.hours / r.population_2020 desc)           as rank_per_capita
from {{ ref('city_reference') }} r
left join totals t
  on t.city = r.city and t.state = r.state
order by hours_per_sq_mi desc