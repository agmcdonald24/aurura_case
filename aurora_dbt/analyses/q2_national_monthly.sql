-- which month it happened: national totals by month
select month,
       sum(construction_events)        as events,
       round(sum(construction_hours))  as hours
from analytics.int_city_month_hours
group by 1
order by 1;