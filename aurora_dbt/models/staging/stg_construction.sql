{{ config(materialized='table') }}

-- One row per distinct construction/closure event.
-- Dedups provider re-pulls, derives duration, rolls NYC's boroughs up to one city, and flags
-- rows whose timestamps or descriptions need handling downstream. Nothing is dropped except
-- exact duplicates; every other judgment is a flag, applied (or not) in the int layer.

with source as (

    select
        id,
        severity,
        start_time,
        end_time,
        start_lat,
        start_lng,
        end_lat,
        end_lng,
        distance_mi,
        description,
        city,
        county,
        state
    from {{ source('raw', 'us_constructions') }}

),

deduped as (

    -- The same event appears more than once when the provider re-pulled it on a
    -- different day: weather columns differ, nothing else does. Keep the lowest id.
    select
        *,
        row_number() over (
            partition by start_time, end_time, start_lat, start_lng, description
            order by id
        ) as dupe_rank
    from source

),

flagged as (

    select
        id as event_id,
        severity,
        start_time,
        end_time,
        extract(epoch from (end_time - start_time)) / 3600.0 as duration_hours,
        start_lat,
        start_lng,
        end_lat,
        end_lng,
        distance_mi,
        description,
        city,
        county,
        state,

        -- NYC's five boroughs are one city; each borough is exactly one NY county
        case
            when state = 'NY'
             and county in ('New York', 'Kings', 'Queens', 'Bronx', 'Richmond')
            then 'New York'
            else city
        end as city_normalized,

        -- seasonal road closures are not roadwork; keep them, flag them
        case
            when description ~* '(winter closure(?!\s*gate)|closed for the (winter|season)|seasonal closure)'
            then 'seasonal_closure'
            else 'construction'
        end as event_type,

        -- still open when the dataset was extracted; duration is truncated
        end_time = '2022-01-01 00:00:00' as is_open_at_extract,

        -- a timestamp shared by many rows is administrative (bulk open/close), not observed
        count(*) over (partition by start_time) >= 100 as is_batch_start,
        count(*) over (partition by end_time)   >= 100 as is_batch_end

    from deduped
    where dupe_rank = 1

)

select * from flagged