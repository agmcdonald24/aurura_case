-- Q2: national totals by month, all cities. Used to date the changes in the source.
select
    month::date                                           as month,
    sum(construction_events)                              as events,
    round(sum(construction_hours))                        as hours
from analytics.int_city_month_hours
group by 1
order by 1;
