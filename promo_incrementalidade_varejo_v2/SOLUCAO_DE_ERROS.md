# Solução de erros comuns

## Erro: arquivo de dependências não encontrado

```text
No such file or directory
```

### Causa provável

O repositório contém apenas o `README.md` ou o terminal está em outra pasta.

### Conferência

```bash
pwd
ls
```

O resultado de `ls` precisa incluir `dependencias.txt` e `preparar_projeto.sh`.

### Correção

Envie todo o conteúdo extraído do ZIP ao GitHub. Depois execute:

```bash
git pull
bash preparar_projeto.sh
```

## Erro: permissão negada ao executar o roteiro

Use:

```bash
bash preparar_projeto.sh
```

Não é necessário executar `./preparar_projeto.sh`.

## Erro: comando dbt não encontrado

Ative o ambiente:

```bash
source .venv/bin/activate
```

Depois confira:

```bash
dbt --version
```

## Erro: perfil dbt não encontrado

Confirme que `profiles.yml` está na raiz e execute com:

```bash
dbt debug --profiles-dir . --profile case_promocoes
```

## Erro: arquivo Parquet não encontrado

Execute, nesta ordem:

```bash
python roteiros/01_baixar_dados.py --modo amostra
python roteiros/02_validar_dados.py
```

Não execute o dbt antes de a validação ser aprovada.

## Download interrompido

Execute novamente o mesmo comando. O roteiro mantém arquivos concluídos e substitui somente arquivos temporários incompletos.

## O dbt terminou com teste reprovado

Não use `--warn-error-options` nem remova o teste para “ficar verde”. Copie a parte do erro e identifique:

- modelo;
- teste;
- quantidade de registros inválidos;
- regra de negócio relacionada.

Uma falha de teste é um diagnóstico, não um incômodo a esconder.

