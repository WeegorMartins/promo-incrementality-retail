"""Valida presença, esquema, volume e sinais de qualidade dos arquivos Parquet."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import duckdb


RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "dados" / "brutos"
MANIFESTO = PASTA / "manifesto_dados.json"
SAIDA = RAIZ / "saidas" / "relatorio_qualidade.json"

COLUNAS_OBRIGATORIAS = {
    "transacoes": {
        "household_id", "store_id", "basket_id", "product_id", "quantity",
        "sales_value", "retail_disc", "coupon_disc", "coupon_match_disc",
        "week", "transaction_timestamp",
    },
    "promocoes": {"product_id", "store_id", "display_location", "mailer_location", "week"},
    "produtos": {
        "product_id", "manufacturer_id", "department", "brand",
        "product_category", "product_type", "package_size",
    },
}


def caminho_sql(caminho: Path) -> str:
    return str(caminho).replace("'", "''")


def main() -> int:
    if not MANIFESTO.exists():
        print("MANIFESTO NÃO ENCONTRADO")
        print("Execute primeiro: python roteiros/01_baixar_dados.py --modo amostra")
        return 1

    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    conexao = duckdb.connect()
    relatorio = {"modo": manifesto["modo"], "status": "aprovado", "tabelas": {}}
    falhas: list[str] = []

    for item in manifesto["tabelas"]:
        nome = item["tabela"]
        arquivo = PASTA / item["arquivo_parquet"]

        if not arquivo.exists():
            falhas.append(f"{nome}: arquivo não encontrado")
            continue

        origem = f"read_parquet('{caminho_sql(arquivo)}')"
        colunas = {
            linha[0] for linha in conexao.execute(f"DESCRIBE SELECT * FROM {origem}").fetchall()
        }
        linhas = conexao.execute(f"SELECT count(*) FROM {origem}").fetchone()[0]
        faltantes = sorted(COLUNAS_OBRIGATORIAS.get(nome, set()) - colunas)

        diagnostico = {
            "linhas": int(linhas),
            "quantidade_colunas": len(colunas),
            "colunas_obrigatorias_faltantes": faltantes,
        }

        if faltantes:
            falhas.append(f"{nome}: faltam colunas {faltantes}")

        if nome == "transacoes":
            resumo = conexao.execute(
                f"""
                SELECT
                    sum(CASE WHEN week NOT BETWEEN 1 AND 53 OR week IS NULL THEN 1 ELSE 0 END),
                    sum(CASE WHEN quantity <= 0 THEN 1 ELSE 0 END),
                    sum(CASE WHEN sales_value < 0 THEN 1 ELSE 0 END),
                    sum(CASE WHEN product_id IS NULL OR store_id IS NULL OR week IS NULL THEN 1 ELSE 0 END)
                FROM {origem}
                """
            ).fetchone()
            diagnostico.update({
                "semanas_invalidas": int(resumo[0] or 0),
                "linhas_quantidade_nao_positiva": int(resumo[1] or 0),
                "linhas_valor_venda_negativo": int(resumo[2] or 0),
                "chaves_nulas": int(resumo[3] or 0),
            })

        if nome == "promocoes":
            resumo = conexao.execute(
                f"""
                SELECT
                    sum(CASE WHEN week NOT BETWEEN 1 AND 53 OR week IS NULL THEN 1 ELSE 0 END),
                    sum(CASE WHEN product_id IS NULL OR store_id IS NULL OR week IS NULL THEN 1 ELSE 0 END),
                    count(*) - count(DISTINCT (product_id, store_id, week))
                FROM {origem}
                """
            ).fetchone()
            diagnostico.update({
                "semanas_invalidas": int(resumo[0] or 0),
                "chaves_nulas": int(resumo[1] or 0),
                "duplicidades_na_chave": int(resumo[2] or 0),
            })

        relatorio["tabelas"][nome] = diagnostico

    if falhas:
        relatorio["status"] = "reprovado"
        relatorio["falhas"] = falhas

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    print(f"\nRelatório salvo em: {SAIDA.relative_to(RAIZ)}")

    if falhas:
        print("\nVALIDAÇÃO REPROVADA. Não avance para o dbt.")
        return 1

    print("\nVALIDAÇÃO APROVADA.")
    print("Próximo comando: dbt build --profiles-dir . --profile case_promocoes")
    return 0


if __name__ == "__main__":
    sys.exit(main())

