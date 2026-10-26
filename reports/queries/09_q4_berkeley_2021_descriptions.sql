-- Q4 validation: the events the model matched to the Berkeley route in 2021, by hours.
select
    e.description,
    count(*)                                              as events,
    round(sum(m.hours_in_year))                           as hours
from analytics.int_route_events m
join analytics.stg_construction e using (event_id)
where m.path_name = 'SF -> Berkley' and m.year = 2021
group by 1
order by hours desc
limit 12;
