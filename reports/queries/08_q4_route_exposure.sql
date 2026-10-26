-- Q4: construction exposure per candidate route, by year and 2017–2021 combined.
select
    path_name,
    distance_mi,
    year,
    events,
    hours,
    hours_per_mile,
    events_per_mile,
    severity_weighted_hours_per_mile,
    long_events,
    rank_hours_per_mile
from analytics.fct_route_exposure
order by year, rank_hours_per_mile;
