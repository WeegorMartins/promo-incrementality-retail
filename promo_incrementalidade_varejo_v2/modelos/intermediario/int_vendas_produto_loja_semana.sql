{{ config(materialized='table') }}

-- A granularidade desta tabela é produto x loja x semana.
-- Mantemos medidas líquidas e medidas positivas separadas para não esconder devoluções.

select
    produto_id,
    loja_id,
    semana,
    sum(quantidade) as unidades_liquidas,
    sum(case when linha_compra_positiva then quantidade else 0 end) as unidades_compradas,
    sum(case when possivel_devolucao then abs(quantidade) else 0 end) as unidades_possivelmente_devolvidas,
    sum(valor_venda) as valor_venda_liquido,
    sum(case when linha_compra_positiva then valor_venda else 0 end) as valor_venda_compras_positivas,
    sum(desconto_varejista) as desconto_varejista_registrado,
    sum(desconto_cupom_fabricante) as desconto_fabricante_registrado,
    sum(desconto_cupom_loja) as desconto_cupom_loja_registrado,
    count(distinct case when linha_compra_positiva then domicilio_id end) as compradores,
    count(distinct case when linha_compra_positiva then cesta_id end) as cestas,
    count(*) as linhas_transacionais,
    sum(case when possivel_devolucao then 1 else 0 end) as linhas_possivel_devolucao
from {{ ref('stg_transacoes') }}
group by 1, 2, 3

