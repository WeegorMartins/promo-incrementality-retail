{{ config(materialized='view') }}

with fonte as (
    select *
    from read_parquet('dados/brutos/produtos.parquet')
)

select
    cast(product_id as varchar) as produto_id,
    cast(manufacturer_id as varchar) as fabricante_id,
    cast(department as varchar) as departamento,
    cast(brand as varchar) as marca,
    cast(product_category as varchar) as categoria_produto,
    cast(product_type as varchar) as tipo_produto,
    cast(package_size as varchar) as tamanho_embalagem
from fonte

