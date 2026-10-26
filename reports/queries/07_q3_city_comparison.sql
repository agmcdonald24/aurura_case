-- Q3: the ten cities normalized by land area and by population (fct_city_comparison).
select
    city,
    state,
    population_2020,
    land_area_sq_mi,
    events,
    round(hours)                                          as hours,
    round(hours_excl_batch)                               as hours_excl_batch,
    round(avg_concurrent_advisories)                      as avg_concurrent,
    round(hours_per_sq_mi)                                as hours_per_sq_mi,
    round(hours_per_100k_residents)                       as hours_per_100k,
    round(events_per_sq_mi::numeric, 1)                   as events_per_sq_mi,
    rank_raw_hours,
    rank_per_sq_mi,
    rank_per_capita
from analytics.fct_city_comparison
order by rank_raw_hours;
