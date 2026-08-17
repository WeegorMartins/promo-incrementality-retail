select
    count(*) as linhas,
    count(distinct produto_id) as produtos,
    count(distinct loja_id) as lojas,
    min(semana) as primeira_semana,
    max(semana) as ultima_semana
from analitico.fct_produto_loja_semana;

select
    mecanica_promocional,
    count(*) as produto_loja_semana,
    sum(unidades_compradas) as unidades,
    round(sum(valor_venda_compras_positivas), 2) as valor_venda
from analitico.fct_produto_loja_semana
group by 1
order by 2 desc;

select
    sum(case when teve_registro_promocional and not teve_venda_observada then 1 else 0 end)
        as semanas_promovidas_sem_venda,
    sum(case when elegivel_painel_inicial then 1 else 0 end)
        as linhas_elegiveis_iniciais,
    sum(case when categoria_produto is null then 1 else 0 end)
        as linhas_sem_categoria
from analitico.fct_produto_loja_semana;

