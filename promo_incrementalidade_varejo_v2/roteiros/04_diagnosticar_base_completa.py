"""Diagnóstico anterior à definição da população e dos episódios promocionais."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import duckdb


RAIZ = Path(__file__).resolve().parents[1]
BANCO = RAIZ / "dados" / "banco" / "case_promocoes.duckdb"
PASTA_SAIDAS = RAIZ / "saidas"


CONSULTAS = {
    "cobertura_do_painel": """
        select
            count(*) as produto_loja_semana,
            sum(case when teve_registro_promocional then 1 else 0 end) as registros_promocionais,
            sum(case when teve_registro_promocional and teve_venda_observada then 1 else 0 end)
                as promocionais_com_compra_no_painel,
            sum(case when teve_registro_promocional and not teve_venda_observada then 1 else 0 end)
                as promocionais_sem_compra_no_painel,
            round(
                100.0 * sum(case when teve_registro_promocional and teve_venda_observada then 1 else 0 end)
                / nullif(sum(case when teve_registro_promocional then 1 else 0 end), 0),
                4
            ) as percentual_promocional_com_compra_no_painel
        from analitico.fct_produto_loja_semana
    """,
    "duplicidades_promocionais": """
        with chaves_repetidas as (
            select
                produto_id,
                loja_id,
                semana,
                linhas_fonte_promocao
            from intermediario.int_promocoes_produto_loja_semana
            where linhas_fonte_promocao > 1
        ),
        grupos as (
            select
                p.produto_id,
                p.loja_id,
                p.semana,
                count(*) as linhas,
                count(distinct p.codigo_exposicao_loja) as codigos_exposicao,
                count(distinct p.codigo_encarte) as codigos_encarte
            from preparacao.stg_promocoes p
            inner join chaves_repetidas c
                on p.produto_id = c.produto_id
               and p.loja_id = c.loja_id
               and p.semana = c.semana
            group by 1, 2, 3
        )
        select
            count(*) as chaves_repetidas,
            sum(linhas - 1) as linhas_extras,
            sum(case when codigos_exposicao > 1 or codigos_encarte > 1 then 1 else 0 end)
                as chaves_com_codigos_diferentes,
            sum(case when codigos_exposicao = 1 and codigos_encarte = 1 then 1 else 0 end)
                as chaves_com_repeticao_exata
        from grupos
    """,
    "distribuicao_quantidades": """
        select
            count(*) as linhas,
            count(*) filter (where quantidade > 0) as linhas_positivas,
            count(*) filter (where quantidade = 0) as linhas_zeradas,
            count(*) filter (where quantidade < 0) as linhas_negativas,
            approx_quantile(quantidade, 0.50) filter (where quantidade > 0) as p50_positivas,
            approx_quantile(quantidade, 0.90) filter (where quantidade > 0) as p90_positivas,
            approx_quantile(quantidade, 0.95) filter (where quantidade > 0) as p95_positivas,
            approx_quantile(quantidade, 0.99) filter (where quantidade > 0) as p99_positivas,
            approx_quantile(quantidade, 0.999) filter (where quantidade > 0) as p999_positivas,
            max(quantidade) as maior_quantidade,
            min(quantidade) as menor_quantidade
        from preparacao.stg_transacoes
    """,
    "frequencia_produto_loja": """
        with pares as (
            select
                produto_id,
                loja_id,
                count(*) filter (where unidades_compradas > 0) as semanas_com_compra,
                sum(unidades_compradas) as unidades_compradas
            from intermediario.int_vendas_produto_loja_semana
            group by 1, 2
        )
        select
            count(*) as pares_produto_loja,
            approx_quantile(semanas_com_compra, 0.50) as p50_semanas_com_compra,
            approx_quantile(semanas_com_compra, 0.75) as p75_semanas_com_compra,
            approx_quantile(semanas_com_compra, 0.90) as p90_semanas_com_compra,
            approx_quantile(semanas_com_compra, 0.95) as p95_semanas_com_compra,
            approx_quantile(semanas_com_compra, 0.99) as p99_semanas_com_compra,
            max(semanas_com_compra) as maior_numero_semanas
        from pares
    """,
    "mecanicas_promocionais": """
        select
            mecanica_promocional,
            count(*) as registros_promocionais,
            sum(case when teve_venda_observada then 1 else 0 end) as registros_com_compra_no_painel,
            round(
                100.0 * sum(case when teve_venda_observada then 1 else 0 end) / count(*),
                4
            ) as percentual_com_compra_no_painel,
            sum(unidades_compradas) as unidades_compradas_pelo_painel,
            round(sum(valor_venda_compras_positivas), 2) as valor_compras_do_painel
        from analitico.fct_produto_loja_semana
        where teve_registro_promocional
        group by 1
        order by 2 desc
    """,
    "elegibilidade_inicial": """
        select
            sum(case when elegivel_painel_inicial then 1 else 0 end) as linhas_elegiveis,
            sum(case when elegivel_painel_inicial and teve_registro_promocional then 1 else 0 end)
                as promocionais_elegiveis,
            sum(case when elegivel_painel_inicial and teve_registro_promocional and teve_venda_observada then 1 else 0 end)
                as promocionais_elegiveis_com_compra,
            count(distinct case when elegivel_painel_inicial then produto_id end) as produtos_elegiveis,
            count(distinct case when elegivel_painel_inicial then loja_id end) as lojas_elegiveis
        from analitico.fct_produto_loja_semana
    """,
}


TOP_QUANTIDADES = """
    select
        t.data_transacao,
        t.domicilio_id,
        t.loja_id,
        t.produto_id,
        t.quantidade,
        t.valor_venda,
        p.departamento,
        p.categoria_produto,
        p.tipo_produto,
        p.tamanho_embalagem
    from preparacao.stg_transacoes t
    left join preparacao.stg_produtos p using (produto_id)
    order by abs(t.quantidade) desc
    limit 100
"""


def registros_serializaveis(tabela):
    return json.loads(tabela.to_json(orient="records", force_ascii=False, date_format="iso"))


def main() -> int:
    if not BANCO.exists():
        print("Banco não encontrado. Execute primeiro o dbt build com a base completa.")
        return 1

    PASTA_SAIDAS.mkdir(parents=True, exist_ok=True)
    pasta_temporaria = RAIZ / "dados" / "banco" / "temporarios_duckdb"
    pasta_temporaria.mkdir(parents=True, exist_ok=True)
    conexao = duckdb.connect(str(BANCO), read_only=True)
    conexao.execute("SET threads = 2")
    conexao.execute("SET memory_limit = '2GB'")
    conexao.execute("SET preserve_insertion_order = false")
    conexao.execute(f"SET temp_directory = '{str(pasta_temporaria).replace(chr(39), chr(39) * 2)}'")
    relatorio = {
        "interpretacao_obrigatoria": (
            "As compras pertencem a um painel de domicílios. Ausência de compra no painel "
            "não equivale a venda zero da loja."
        ),
        "diagnosticos": {},
    }

    print("DIAGNÓSTICO DA BASE COMPLETA — VERSÃO OTIMIZADA")
    print("IMPORTANTE: o resultado mede compras observadas no painel de domicílios.\n")

    for nome, consulta in CONSULTAS.items():
        tabela = conexao.execute(consulta).df()
        relatorio["diagnosticos"][nome] = registros_serializaveis(tabela)
        print(nome.upper().replace("_", " "))
        print(tabela.to_string(index=False))
        print()

    extremos = conexao.execute(TOP_QUANTIDADES).df()
    caminho_extremos = PASTA_SAIDAS / "100_maiores_quantidades.csv"
    extremos.to_csv(caminho_extremos, index=False)

    caminho_relatorio = PASTA_SAIDAS / "diagnostico_base_completa.json"
    caminho_relatorio.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("ARQUIVOS GERADOS")
    print(f"- {caminho_relatorio.relative_to(RAIZ)}")
    print(f"- {caminho_extremos.relative_to(RAIZ)}")
    print("\nDIAGNÓSTICO CONCLUÍDO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
