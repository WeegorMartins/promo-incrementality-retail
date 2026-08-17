{{ config(materialized='view') }}

-- Esta camada preserva os valores originais e apenas padroniza nomes e tipos.
-- Registros de devolução ou quantidade zero não são apagados silenciosamente.

with fonte as (
    select *
    from read_parquet('dados/brutos/transacoes.parquet')
)

select
    cast(household_id as varchar) as domicilio_id,
    cast(store_id as varchar) as loja_id,
    cast(basket_id as varchar) as cesta_id,
    cast(product_id as varchar) as produto_id,
    cast(quantity as double) as quantidade,
    cast(sales_value as double) as valor_venda,
    coalesce(cast(retail_disc as double), 0) as desconto_varejista,
    coalesce(cast(coupon_disc as double), 0) as desconto_cupom_fabricante,
    coalesce(cast(coupon_match_disc as double), 0) as desconto_cupom_loja,
    cast(week as integer) as semana,
    cast(transaction_timestamp as timestamp) as data_hora_transacao,
    cast(transaction_timestamp as date) as data_transacao,
    case when quantity < 0 or sales_value < 0 then true else false end as possivel_devolucao,
    case when quantity > 0 and sales_value >= 0 then true else false end as linha_compra_positiva
from fonte

