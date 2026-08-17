"""Executa uma auditoria curta depois da construção dos modelos dbt."""

from pathlib import Path
import sys

import duckdb


RAIZ = Path(__file__).resolve().parents[1]
BANCO = RAIZ / "dados" / "banco" / "case_promocoes.duckdb"
ARQUIVO_SQL = RAIZ / "sql" / "01_auditoria_modelos.sql"


def main() -> int:
    if not BANCO.exists():
        print("Banco não encontrado. Execute primeiro o dbt build.")
        return 1

    sql = ARQUIVO_SQL.read_text(encoding="utf-8")
    conexao = duckdb.connect(str(BANCO), read_only=True)
    blocos = [bloco.strip() for bloco in sql.split(";") if bloco.strip()]

    print("AUDITORIA DOS MODELOS")
    for numero, bloco in enumerate(blocos, start=1):
        resultado = conexao.execute(bloco)
        print(f"\nConsulta {numero}")
        print(resultado.df().to_string(index=False))

    print("\nAUDITORIA CONCLUÍDA")
    return 0


if __name__ == "__main__":
    sys.exit(main())

