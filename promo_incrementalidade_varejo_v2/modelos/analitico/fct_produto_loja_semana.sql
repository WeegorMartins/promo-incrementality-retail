{{ config(materialized='table') }}

-- Esta tabela inclui semanas promovidas sem venda observada.
-- Ainda não constitui, sozinha, um painel causal válido.

with chaves as (
    select produto_id, loja_id, semana
    from {{ ref('int_vendas_produto_loja_semana') }}
    union
    select produto_id, loja_id, semana
    from {{ ref('int_promocoes_produto_loja_semana') }}
),

base as (
    select
        c.produto_id,
        c.loja_id,
        c.semana,
        coalesce(v.unidades_liquidas, 0) as unidades_liquidas,
        coalesce(v.unidades_compradas, 0) as unidades_compradas,
        coalesce(v.unidades_possivelmente_devolvidas, 0) as unidades_possivelmente_devolvidas,
        coalesce(v.valor_venda_liquido, 0) as valor_venda_liquido,
        coalesce(v.valor_venda_compras_positivas, 0) as valor_venda_compras_positivas,
        coalesce(v.desconto_varejista_registrado, 0) as desconto_varejista_registrado,
        coalesce(v.desconto_fabricante_registrado, 0) as desconto_fabricante_registrado,
        coalesce(v.desconto_cupom_loja_registrado, 0) as desconto_cupom_loja_registrado,
        coalesce(v.compradores, 0) as compradores,
        coalesce(v.cestas, 0) as cestas,
        coalesce(p.teve_exposicao_loja, false) as teve_exposicao_loja,
        coalesce(p.teve_encarte, false) as teve_encarte,
        coalesce(p.mecanica_promocional, 'sem_mecanica_identificada') as mecanica_promocional,
        v.produto_id is not null as teve_venda_observada,
        p.produto_id is not null as teve_registro_promocional
    from chaves c
    left join {{ ref('int_vendas_produto_loja_semana') }} v using (produto_id, loja_id, semana)
    left join {{ ref('int_promocoes_produto_loja_semana') }} p using (produto_id, loja_id, semana)
)

select
    b.*,
    pr.departamento,
    pr.marca,
    pr.categoria_produto,
    pr.tipo_produto,
    e.semanas_com_venda,
    e.semanas_com_promocao,
    coalesce(e.elegivel_painel_inicial, false) as elegivel_painel_inicial
from base b
left join {{ ref('stg_produtos') }} pr using (produto_id)
left join {{ ref('int_elegibilidade_produto_loja') }} e using (produto_id, loja_id)

