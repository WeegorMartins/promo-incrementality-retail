"""Diagnostica a variável quantidade após separar registros de combustível.

Este roteiro não altera os dados nem o banco. Ele:
1. compara combustível e demais produtos;
2. mede a distribuição de quantidade fora de combustível;
3. identifica os tipos de produto que ainda concentram valores altos;
4. exporta as 100 maiores quantidades fora de combustível para revisão.
"""

from pathlib import Path

import duckdb


PASTA_RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_BANCO = PASTA_RAIZ / "dados" / "banco" / "case_promocoes.duckdb"
PASTA_SAIDAS = PASTA_RAIZ / "saidas"
ARQUIVO_SAIDA = PASTA_SAIDAS / "100_maiores_quantidades_sem_combustivel.csv"


def imprimir_tabela(titulo: str, resultado) -> None:
    print(f"\n{titulo}")
    print(resultado.fetchdf().to_string(index=False))


def main() -> None:
    if not CAMINHO_BANCO.exists():
        raise FileNotFoundError(
            f"Banco não encontrado em: {CAMINHO_BANCO}\n"
            "Execute antes a construção completa dos modelos."
        )

    PASTA_SAIDAS.mkdir(parents=True, exist_ok=True)

    conexao = duckdb.connect(str(CAMINHO_BANCO), read_only=True)
    conexao.execute("SET memory_limit = '3GB'")
    conexao.execute("SET threads = 4")

    print("DIAGNÓSTICO DE QUANTIDADES SEM COMBUSTÍVEL")
    print("O banco será somente consultado; nenhum dado será modificado.")

    imprimir_tabela(
        "1. COMPARAÇÃO ENTRE COMBUSTÍVEL E DEMAIS PRODUTOS",
        conexao.execute(
            """
            select
                case
                    when upper(trim(coalesce(p.tipo_produto, ''))) =
                         'GASOLINE-REG UNLEADED'
                    then 'combustivel'
                    else 'demais_produtos'
                end as grupo,
                count(*) as linhas,
                count(distinct t.domicilio_id) as domicilios,
                count(distinct t.produto_id) as produtos,
                sum(t.quantidade) as quantidade_registrada,
                sum(t.valor_venda) as valor_venda,
                min(t.quantidade) as menor_quantidade,
                median(t.quantidade) as mediana_quantidade,
                max(t.quantidade) as maior_quantidade
            from principal.stg_transacoes t
            left join principal.stg_produtos p using (produto_id)
            group by 1
            order by 1
            """
        ),
    )

    imprimir_tabela(
        "2. DISTRIBUIÇÃO DE QUANTIDADE — DEMAIS PRODUTOS",
        conexao.execute(
            """
            select
                count(*) as linhas,
                count_if(t.quantidade > 0) as linhas_positivas,
                count_if(t.quantidade = 0) as linhas_zeradas,
                count_if(t.quantidade < 0) as linhas_negativas,
                quantile_cont(t.quantidade, 0.50) as p50,
                quantile_cont(t.quantidade, 0.90) as p90,
                quantile_cont(t.quantidade, 0.95) as p95,
                quantile_cont(t.quantidade, 0.99) as p99,
                quantile_cont(t.quantidade, 0.999) as p999,
                max(t.quantidade) as maior_quantidade
            from principal.stg_transacoes t
            left join principal.stg_produtos p using (produto_id)
            where upper(trim(coalesce(p.tipo_produto, ''))) <>
                  'GASOLINE-REG UNLEADED'
            """
        ),
    )

    imprimir_tabela(
        "3. TIPOS DE PRODUTO COM MAIORES QUANTIDADES",
        conexao.execute(
            """
            select
                coalesce(p.departamento, 'SEM DEPARTAMENTO') as departamento,
                coalesce(p.categoria_produto, 'SEM CATEGORIA') as categoria_produto,
                coalesce(p.tipo_produto, 'SEM TIPO') as tipo_produto,
                count(*) as linhas,
                quantile_cont(t.quantidade, 0.99) as p99_quantidade,
                max(t.quantidade) as maior_quantidade,
                sum(t.valor_venda) as valor_venda
            from principal.stg_transacoes t
            left join principal.stg_produtos p using (produto_id)
            where upper(trim(coalesce(p.tipo_produto, ''))) <>
                  'GASOLINE-REG UNLEADED'
            group by 1, 2, 3
            having count(*) >= 20
            order by maior_quantidade desc, linhas desc
            limit 30
            """
        ),
    )

    conexao.execute(
        """
        copy (
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
            from principal.stg_transacoes t
            left join principal.stg_produtos p using (produto_id)
            where upper(trim(coalesce(p.tipo_produto, ''))) <>
                  'GASOLINE-REG UNLEADED'
            order by t.quantidade desc
            limit 100
        ) to ? (header, delimiter ',')
        """,
        [str(ARQUIVO_SAIDA)],
    )

    conexao.close()

    print("\n4. ARQUIVO GERADO")
    print(f"- {ARQUIVO_SAIDA.relative_to(PASTA_RAIZ)}")
    print("\nDIAGNÓSTICO CONCLUÍDO")


if __name__ == "__main__":
    main()
