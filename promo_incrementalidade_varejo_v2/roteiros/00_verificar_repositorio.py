"""Confere a estrutura mínima antes de qualquer instalação ou download."""

from pathlib import Path
import sys


RAIZ = Path(__file__).resolve().parents[1]

ARQUIVOS_OBRIGATORIOS = [
    "LEIA_PRIMEIRO.md",
    "README.md",
    "GUIA_MESTRE.md",
    "dependencias.txt",
    "preparar_projeto.sh",
    "dbt_project.yml",
    "profiles.yml",
    "roteiros/01_baixar_dados.py",
    "roteiros/02_validar_dados.py",
    "modelos/preparacao/stg_transacoes.sql",
    "modelos/preparacao/stg_promocoes.sql",
    "modelos/analitico/fct_produto_loja_semana.sql",
]


def main() -> int:
    faltantes = [nome for nome in ARQUIVOS_OBRIGATORIOS if not (RAIZ / nome).exists()]

    print(f"Pasta conferida: {RAIZ}")

    if faltantes:
        print("\nREPOSITÓRIO INCOMPLETO")
        print("Os seguintes arquivos ou pastas não foram encontrados:")
        for nome in faltantes:
            print(f"  - {nome}")
        print("\nCausa mais provável:")
        print("  Apenas o README foi enviado ao GitHub, ou o terminal não está na raiz do projeto.")
        print("\nComo corrigir:")
        print("  1. Extraia o ZIP no computador.")
        print("  2. Envie TODO o conteúdo da pasta extraída ao repositório.")
        print("  3. Volte à raiz do repositório e execute novamente:")
        print("     bash preparar_projeto.sh")
        return 1

    print("ESTRUTURA APROVADA: todos os arquivos mínimos foram encontrados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
