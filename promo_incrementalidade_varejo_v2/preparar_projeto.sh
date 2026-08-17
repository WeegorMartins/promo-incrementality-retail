#!/usr/bin/env bash
set -euo pipefail

echo "[1/5] Conferindo se você está na raiz correta do projeto..."
python3 roteiros/00_verificar_repositorio.py

echo "[2/5] Criando o ambiente virtual, caso ainda não exista..."
python3 -m venv .venv

echo "[3/5] Ativando o ambiente virtual..."
source .venv/bin/activate

echo "[4/5] Instalando as dependências..."
python -m pip install --upgrade pip
python -m pip install -r dependencias.txt

echo "[5/5] Conferindo as ferramentas instaladas..."
python --version
python -c "import duckdb; print('DuckDB', duckdb.__version__)"
dbt --version

echo
echo "PREPARAÇÃO CONCLUÍDA"
echo "Próximo comando: source .venv/bin/activate"
echo "Depois, abra GUIA_MESTRE.md e execute apenas a Fase 2."

