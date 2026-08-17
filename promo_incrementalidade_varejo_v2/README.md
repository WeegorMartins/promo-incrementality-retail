# Quando vender mais não significa criar valor

## Análise da incrementalidade de promoções no varejo

Projeto de portfólio para demonstrar atuação de nível sênior em análise de dados, com foco em uma decisão real de negócio:

> Quais promoções devem ser ampliadas, mantidas de forma direcionada, redesenhadas, testadas novamente ou interrompidas quando consideramos vendas adicionais, desconto, antecipação de compras e canibalização?

O projeto utiliza dados públicos do estudo **Complete Journey**, disponibilizado pela 84.51° e organizado no pacote `completejourney`.

## O que este projeto demonstra

- transformação de uma pergunta vaga em decisão;
- definição de métricas e granularidade;
- diagnóstico de qualidade dos dados;
- SQL analítico e modelagem com dbt;
- Python para análise estatística;
- desenho observacional com limites explícitos;
- cenários financeiros sem inventar custos;
- comunicação executiva no Power BI;
- documentação das escolhas e dos riscos.

## Ferramentas gratuitas

- GitHub e GitHub Codespaces;
- Python;
- DuckDB;
- dbt Core com adaptador DuckDB;
- arquivos Parquet;
- Power BI Desktop;
- Git.

## Comece aqui

1. Leia `LEIA_PRIMEIRO.md`.
2. Execute `bash preparar_projeto.sh`.
3. Siga `GUIA_MESTRE.md` sem pular os critérios de avanço.
4. Marque o progresso em `CHECKLIST_DE_AVANCO.md`.

## Regra de credibilidade

O repositório não apresenta resultados antes da execução dos dados. Correlação não será chamada de causalidade, resgate de cupom não será tratado como exposição aleatória e margem real não será inventada.

## Escolha de versão do dbt

O padrão do projeto é dbt Core 1.12 com o adaptador DuckDB 1.11. Em agosto de 2026, o dbt v2/Fusion é a direção mais nova, mas a execução local com DuckDB ainda está indicada como beta. Para este case, reprodutibilidade pesa mais do que adotar uma prévia sem ganho na decisão de negócio.
