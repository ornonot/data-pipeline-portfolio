with staging_data as (

    select
        *
    from {{ ref('stg_portfolio') }}

)

select
    *
from staging_data