{{ config(materialized='table') }}

-- A agregação protege o modelo contra eventual duplicidade na fonte.

select
    produto_id,
    loja_id,
    semana,
    bool_or(teve_exposicao_loja) as teve_exposicao_loja,
    bool_or(teve_encarte) as teve_encarte,
    case
        when bool_or(teve_exposicao_loja) and bool_or(teve_encarte) then 'exposicao_e_encarte'
        when bool_or(teve_exposicao_loja) then 'somente_exposicao'
        when bool_or(teve_encarte) then 'somente_encarte'
        else 'sem_mecanica_identificada'
    end as mecanica_promocional,
    count(*) as linhas_fonte_promocao
from {{ ref('stg_promocoes') }}
group by 1, 2, 3

