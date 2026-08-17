# LEIA PRIMEIRO — início sem erro

Este é o ponto de entrada do projeto.

## O que aconteceu na tentativa anterior

O erro exibido foi:

```text
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

Isso significa que o comando estava correto, mas o arquivo `requirements.txt` não estava no repositório. Pela imagem, o repositório continha apenas `README.md` e a pasta `.venv` criada durante a tentativa.

## Antes de abrir o Codespaces

1. Baixe e extraia o arquivo ZIP deste projeto no computador.
2. Abra a pasta extraída `promo_incrementalidade_varejo_v2`.
3. No GitHub, abra o repositório do projeto.
4. Clique em `Add file` > `Upload files`.
5. Arraste **todo o conteúdo de dentro da pasta extraída**, e não apenas o `README.md`.
6. Confirme o envio dos arquivos.
7. Abra um Codespace novo ou execute `git pull` no Codespace atual.

## Conferência visual obrigatória

Antes de digitar qualquer comando, o painel esquerdo do VS Code precisa mostrar, no mínimo:

```text
documentacao/
modelos/
roteiros/
sql/
LEIA_PRIMEIRO.md
README.md
dbt_project.yml
dependencias.txt
profiles.yml
preparar_projeto.sh
```

Se aparecer apenas `README.md`, não avance: os arquivos não foram enviados.

## Único comando inicial

No terminal do Codespaces, copie e cole:

```bash
bash preparar_projeto.sh
```

O comando:

- verifica se o repositório está completo;
- cria o ambiente virtual;
- instala as dependências gratuitas;
- confere as versões instaladas;
- não baixa os dados ainda.

## Sinal de sucesso

Ao final, deve aparecer:

```text
PREPARAÇÃO CONCLUÍDA
Próximo comando: source .venv/bin/activate
```

Depois disso, siga o arquivo `GUIA_MESTRE.md`, uma fase por vez.

Se algo não corresponder às mensagens esperadas, consulte `SOLUCAO_DE_ERROS.md` e não avance por tentativa e erro.
