select
    produto_id,
    loja_id,
    semana,
    count(*) as quantidade
from {{ ref('fct_produto_loja_semana') }}
group by 1, 2, 3
having count(*) > 1

