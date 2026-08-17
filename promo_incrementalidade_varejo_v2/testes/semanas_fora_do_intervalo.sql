select *
from {{ ref('fct_produto_loja_semana') }}
where semana not between 1 and 53

