-- Row counts at each layer, plus the Bay Area event-length buckets used by Q4.
select 'raw rows'                     as measure, count(*)::bigint as value from raw.us_constructions
union all
select 'staged events',                 count(*) from analytics.stg_construction
union all
select 'duplicates removed',            (select count(*) from raw.us_constructions) - count(*) from analytics.stg_construction
union all
select 'seasonal closures',             count(*) from analytics.stg_construction where event_type = 'seasonal_closure'
union all
select 'bay area events',               count(*) from analytics.stg_construction
                                        where start_lat between 37.4 and 38.1 and start_lng between -122.7 and -121.9
union all
select 'bay area events over 5 miles',  count(*) from analytics.stg_construction
                                        where start_lat between 37.4 and 38.1 and start_lng between -122.7 and -121.9
                                          and distance_mi > 5;
