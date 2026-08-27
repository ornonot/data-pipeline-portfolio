with source_data as (

    select
        *
    from {{ source('raw_weather', 'weather_forecast') }}

)

select
    *
from source_data