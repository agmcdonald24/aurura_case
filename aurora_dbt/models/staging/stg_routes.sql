{{ config(materialized='table') }}

-- One row per vertex of each candidate route, parsed from the WKT in the sf_paths seed.
-- Vertices are a few tens of metres apart, so "within 100 m of a vertex" is effectively
-- "within 100 m of the route". cell_x / cell_y are ~100 m grid cells used to make the
-- distance join cheap: only points in the same or a neighbouring cell get compared.

with routes as (

    select
        path_name,
        distance_mi,
        regexp_replace(path_wkt, '^LINESTRING \(|\)$', '', 'g') as coord_list
    from {{ ref('sf_paths') }}

),

vertices as (

    select
        r.path_name,
        r.distance_mi,
        v.ord                                              as vertex_num,
        split_part(trim(v.pair), ' ', 1)::double precision as lng,
        split_part(trim(v.pair), ' ', 2)::double precision as lat
    from routes r
    cross join lateral unnest(string_to_array(r.coord_list, ',')) with ordinality as v(pair, ord)

)

select
    path_name,
    distance_mi,
    vertex_num,
    lng,
    lat,
    floor(lng / 0.00115)::int as cell_x,
    floor(lat / 0.0009)::int  as cell_y
from vertices