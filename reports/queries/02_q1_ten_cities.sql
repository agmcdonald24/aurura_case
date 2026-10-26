-- Q1 / Q3: the ten cities named in the brief, 2017–2021 totals.
-- avg_concurrent = hours / (5 years × 8,760 hours): advisories active at any moment, on average.
select
    city,
    state,
    sum(construction_events)                              as events,
    round(sum(construction_hours))                        as hours,
    round(sum(construction_hours_excl_batch))             as hours_excl_batch,
    round(sum(construction_hours) / (5 * 8760))           as avg_concurrent
from analytics.int_city_month_hours
where (city, state) in (
    ('New York','NY'), ('Los Angeles','CA'), ('Chicago','IL'), ('Houston','TX'),
    ('Phoenix','AZ'), ('San Antonio','TX'), ('Philadelphia','PA'), ('San Diego','CA'),
    ('Dallas','TX'), ('Austin','TX')
)
group by 1, 2
order by hours desc nulls last;
