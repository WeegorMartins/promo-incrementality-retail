{{ config(materialized='table') }}

-- Não existe uma tabela de estoque ou sortimento. Portanto, presença comercial
-- é aproximada pelo histórico observado e deve ser tratada como limitação.

with vendas as (
    select
        produto_id,
        loja_id,
        count(distinct semana) as semanas_com_venda,
        min(semana) as primeira_semana_venda,
        max(semana) as ultima_semana_venda
    from {{ ref('int_vendas_produto_loja_semana') }}
    where unidades_compradas > 0
    group by 1, 2
),

promocoes as (
    select
        produto_id,
        loja_id,
        count(distinct semana) as semanas_com_promocao
    from {{ ref('int_promocoes_produto_loja_semana') }}
    where mecanica_promocional <> 'sem_mecanica_identificada'
    group by 1, 2
)

select
    v.produto_id,
    v.loja_id,
    v.semanas_com_venda,
    coalesce(p.semanas_com_promocao, 0) as semanas_com_promocao,
    v.primeira_semana_venda,
    v.ultima_semana_venda,
    v.semanas_com_venda >= {{ var('minimo_semanas_com_venda') }} as elegivel_painel_inicial,
    'Aproximação por semanas com venda; estoque e sortimento não observados' as ressalva_elegibilidade
from vendas v
left join promocoes p
    on v.produto_id = p.produto_id
   and v.loja_id = p.loja_id

