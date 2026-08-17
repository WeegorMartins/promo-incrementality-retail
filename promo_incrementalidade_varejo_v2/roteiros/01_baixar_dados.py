"""Baixa os dados originais do projeto Complete Journey e converte para Parquet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd
import pyreadr
import requests


RAIZ = Path(__file__).resolve().parents[1]
PASTA_ORIGINAIS = RAIZ / "dados" / "originais"
PASTA_BRUTOS = RAIZ / "dados" / "brutos"
BASE_URL = "https://raw.githubusercontent.com/bradleyboehmke/completejourney/master/data"

TABELAS_FIXAS = {
    "produtos": "products.rda",
    "domicilios": "demographics.rda",
    "campanhas": "campaigns.rda",
    "descricoes_campanhas": "campaign_descriptions.rda",
    "cupons": "coupons.rda",
    "resgates_cupons": "coupon_redemptions.rda",
}

TABELAS_POR_MODO = {
    "amostra": {
        "transacoes": "transactions_sample.rda",
        "promocoes": "promotions_sample.rda",
    },
    "completo": {
        "transacoes": "transactions.rds",
        "promocoes": "promotions.rds",
    },
}


def calcular_sha256(caminho: Path) -> str:
    resumo = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            resumo.update(bloco)
    return resumo.hexdigest()


def baixar(url: str, destino: Path) -> None:
    if destino.exists() and destino.stat().st_size > 0:
        print(f"  Já existe: {destino.name}")
        return

    temporario = destino.with_suffix(destino.suffix + ".parcial")
    print(f"  Baixando: {destino.name}")

    with requests.get(url, stream=True, timeout=120) as resposta:
        resposta.raise_for_status()
        with temporario.open("wb") as arquivo:
            for bloco in resposta.iter_content(chunk_size=1024 * 1024):
                if bloco:
                    arquivo.write(bloco)

    temporario.replace(destino)


def ler_arquivo_r(caminho: Path) -> pd.DataFrame:
    objetos = pyreadr.read_r(str(caminho))
    if not objetos:
        raise ValueError(f"Nenhum objeto tabular encontrado em {caminho.name}")
    tabela = next(iter(objetos.values()))
    if not isinstance(tabela, pd.DataFrame):
        raise TypeError(f"O conteúdo de {caminho.name} não foi convertido em tabela.")
    return tabela


def preparar_tipos(tabela: pd.DataFrame) -> pd.DataFrame:
    tabela = tabela.copy()
    tabela.columns = [str(coluna).strip().lower() for coluna in tabela.columns]

    for coluna in tabela.select_dtypes(include=["category"]).columns:
        tabela[coluna] = tabela[coluna].astype("string")

    for coluna in tabela.select_dtypes(include=["object"]).columns:
        tabela[coluna] = tabela[coluna].astype("string")

    return tabela


def converter(nome_tabela: str, origem: Path, destino: Path) -> dict[str, Any]:
    print(f"  Convertendo {nome_tabela} para Parquet...")
    tabela = preparar_tipos(ler_arquivo_r(origem))
    tabela.to_parquet(destino, index=False, compression="zstd")
    return {
        "tabela": nome_tabela,
        "arquivo_origem": origem.name,
        "arquivo_parquet": destino.name,
        "linhas": int(len(tabela)),
        "colunas": list(tabela.columns),
        "sha256_origem": calcular_sha256(origem),
        "sha256_parquet": calcular_sha256(destino),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa e converte os dados do case.")
    parser.add_argument(
        "--modo",
        choices=["amostra", "completo"],
        default="amostra",
        help="Use amostra primeiro. O modo completo contém mais de 20 milhões de exposições.",
    )
    parser.add_argument(
        "--refazer",
        action="store_true",
        help="Reconverte arquivos já existentes. Não baixa novamente arquivos válidos.",
    )
    args = parser.parse_args()

    PASTA_ORIGINAIS.mkdir(parents=True, exist_ok=True)
    PASTA_BRUTOS.mkdir(parents=True, exist_ok=True)

    tabelas = {**TABELAS_FIXAS, **TABELAS_POR_MODO[args.modo]}
    manifesto: dict[str, Any] = {"modo": args.modo, "tabelas": []}

    print(f"MODO SELECIONADO: {args.modo.upper()}")
    print("Etapa 1 de 2 — obtenção dos arquivos originais")

    for arquivo in tabelas.values():
        baixar(f"{BASE_URL}/{arquivo}", PASTA_ORIGINAIS / arquivo)

    print("Etapa 2 de 2 — conversão para Parquet")

    for nome_tabela, arquivo in tabelas.items():
        origem = PASTA_ORIGINAIS / arquivo
        destino = PASTA_BRUTOS / f"{nome_tabela}.parquet"
        if destino.exists() and not args.refazer:
            print(f"  Parquet já existe: {destino.name}")
            tabela = preparar_tipos(ler_arquivo_r(origem))
            registro = {
                "tabela": nome_tabela,
                "arquivo_origem": origem.name,
                "arquivo_parquet": destino.name,
                "linhas": int(len(tabela)),
                "colunas": list(tabela.columns),
                "sha256_origem": calcular_sha256(origem),
                "sha256_parquet": calcular_sha256(destino),
            }
        else:
            registro = converter(nome_tabela, origem, destino)
        manifesto["tabelas"].append(registro)

    caminho_manifesto = PASTA_BRUTOS / "manifesto_dados.json"
    caminho_manifesto.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\nDOWNLOAD E CONVERSÃO CONCLUÍDOS")
    print(f"Manifesto: {caminho_manifesto.relative_to(RAIZ)}")
    print("Agora execute: python roteiros/02_validar_dados.py")


if __name__ == "__main__":
    main()

