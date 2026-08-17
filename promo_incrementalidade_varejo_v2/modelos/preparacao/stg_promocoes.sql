{{ config(materialized='view') }}

with fonte as (
    select *
    from read_parquet('dados/brutos/promocoes.parquet')
)

select
    cast(product_id as varchar) as produto_id,
    cast(store_id as varchar) as loja_id,
    cast(week as integer) as semana,
    coalesce(cast(display_location as varchar), '0') as codigo_exposicao_loja,
    coalesce(cast(mailer_location as varchar), '0') as codigo_encarte,
    codigo_exposicao_loja <> '0' as teve_exposicao_loja,
    codigo_encarte <> '0' as teve_encarte,
    case
        when codigo_exposicao_loja <> '0' and codigo_encarte <> '0' then 'exposicao_e_encarte'
        when codigo_exposicao_loja <> '0' then 'somente_exposicao'
        when codigo_encarte <> '0' then 'somente_encarte'
        else 'sem_mecanica_identificada'
    end as mecanica_promocional
from fonte

