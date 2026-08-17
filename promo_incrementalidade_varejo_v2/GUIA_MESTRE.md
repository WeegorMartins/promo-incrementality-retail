# Guia mestre — case sênior de eficiência promocional

Este documento organiza o projeto inteiro. Execute uma fase por vez. Não avance apenas porque o comando terminou: avance quando o **critério de saída** estiver atendido.

## Visão geral

| Fase | Pergunta respondida | Entregável | Pode avançar quando... |
|---:|---|---|---|
| 0 | O repositório está completo e o ambiente funciona? | ambiente preparado | a conferência e as versões terminarem sem erro |
| 1 | Qual decisão de negócio será tomada? | contrato de análise | decisão, unidade, métricas e limites estiverem claros |
| 2 | Os dados são íntegros e suficientes? | relatório de qualidade | arquivos, colunas e chaves forem validados |
| 3 | As métricas são reproduzíveis? | modelos dbt | testes passarem e granularidade for única |
| 4 | O que ocorre descritivamente? | diagnóstico SQL/Python | cada gráfico responder uma hipótese |
| 5 | O que é um episódio promocional comparável? | base de episódios | tratamento, janelas e elegibilidade estiverem definidos |
| 6 | Qual comparação reduz o viés? | desenho observacional | pré-tendências e sobreposição forem aceitáveis |
| 7 | Qual é o efeito estimado e sua incerteza? | estimação principal | efeito, intervalo e robustez forem apresentados |
| 8 | Houve canibalização ou antecipação? | efeitos indiretos | SKU, categoria e pós-promoção forem comparados |
| 9 | Em quais cenários há valor econômico? | cenários financeiros | decisão for robusta a margens plausíveis |
| 10 | O que deve ser feito? | matriz de decisão | cada grupo receber uma ação e uma justificativa |
| 11 | Como a liderança consumirá a análise? | painel Power BI | cada página apoiar uma decisão |
| 12 | Como publicar sem exagerar? | README e narrativa | evidência e limitação estiverem separadas |
| 13 | Como defender o case? | roteiro de entrevista | você conseguir explicar escolhas e alternativas |

---

# Fase 0 — preparar e conferir o ambiente

## Objetivo

Eliminar problemas de estrutura antes de instalar ferramentas ou baixar arquivos.

## Passo 0.1 — conferir o painel esquerdo

Veja `LEIA_PRIMEIRO.md`. Se aparecer apenas `README.md`, o repositório está incompleto.

## Passo 0.2 — preparar tudo com um comando

```bash
bash preparar_projeto.sh
```

## Por que fazer assim

O roteiro interrompe a execução imediatamente se faltar qualquer arquivo. Isso evita receber um erro técnico distante da causa real.

## Como validar

Procure a mensagem:

```text
PREPARAÇÃO CONCLUÍDA
```

## Erros comuns

- enviar somente o `README.md`;
- enviar o ZIP sem extrair;
- executar o terminal fora da raiz do repositório;
- esquecer de ativar `.venv` ao abrir um terminal novo.

## Como explicar em entrevista

> “Estruturei uma verificação anterior à instalação para evitar falhas silenciosas de ambiente. O projeto separa falha de estrutura, falha de dependência e falha de dados, facilitando diagnóstico e reprodução.”

---

# Fase 1 — fechar o problema de negócio

## Objetivo

Evitar começar por gráficos sem saber qual decisão será influenciada.

## Passo 1.1 — ler os documentos

Abra, nesta ordem:

1. `documentacao/01_contexto_negocio.md`;
2. `documentacao/02_contrato_analise.yml`;
3. `documentacao/03_arvore_metricas.md`;
4. `documentacao/04_dicionario_metricas.md`.

Não altere a pergunta central na primeira execução. Primeiro conclua uma versão coerente do projeto.

## Decisão principal

Para cada combinação de mecânica promocional, categoria e segmento, recomendar:

- ampliar;
- manter de forma direcionada;
- redesenhar;
- realizar experimento controlado;
- interromper.

## Critério de saída

Você precisa conseguir responder, sem abrir o código:

- quem decide;
- qual unidade recebe a decisão;
- qual resultado principal importa;
- quais efeitos indesejados serão monitorados;
- o que os dados não permitem afirmar.

---

# Fase 2 — baixar e validar os dados

## Objetivo

Confirmar o processo com uma amostra antes de processar a base completa.

## Passo 2.1 — ativar o ambiente

Sempre que abrir um terminal novo:

```bash
source .venv/bin/activate
```

O início da linha do terminal deve mostrar `(.venv)`.

## Passo 2.2 — baixar a amostra

```bash
python roteiros/01_baixar_dados.py --modo amostra
```

O roteiro usa arquivos originais do projeto `completejourney`, converte as tabelas para Parquet e cria um manifesto com volume, colunas e resumo criptográfico dos arquivos.

## Passo 2.3 — validar a amostra

```bash
python roteiros/02_validar_dados.py
```

## O que validar no resultado

- `transacoes`: aproximadamente 75 mil linhas na amostra;
- `promocoes`: aproximadamente 360 mil linhas na amostra;
- semanas entre 1 e 53;
- nenhuma coluna obrigatória faltante;
- chaves nulas reportadas;
- quantidades não positivas e valores negativos reportados, mas não apagados.

Quantidade zero ou negativa não é removida automaticamente. Pode representar devolução, ajuste ou item técnico. Primeiro diagnosticamos; depois definimos regra.

## Critério de saída

O terminal precisa mostrar:

```text
VALIDAÇÃO APROVADA
```

Se aparecer `VALIDAÇÃO REPROVADA`, pare e envie o conteúdo de `saidas/relatorio_qualidade.json` para análise.

## Como isso ocorre em uma empresa

É comum uma área pedir “vendas” enquanto a base contém devoluções, cancelamentos e itens zerados. A decisão sênior é preservar a informação original, criar indicadores e combinar a regra com o dono do dado.

## Como explicar em entrevista

> “Não excluí linhas negativas por conveniência. Preservei valores brutos, medi a incidência e criei métricas positivas e líquidas separadas. Isso evita transformar uma hipótese sobre devolução em uma regra oculta.”

---

# Fase 3 — construir e testar as métricas

## Objetivo

Transformar arquivos brutos em tabelas analíticas reproduzíveis e auditáveis.

## Passo 3.1 — testar a conexão

```bash
dbt debug --profiles-dir . --profile case_promocoes
```

Procure `All checks passed`.

## Passo 3.2 — construir os modelos

```bash
dbt build --profiles-dir . --profile case_promocoes
```

## Passo 3.3 — auditar o resultado

```bash
python roteiros/03_auditar_banco.py
```

## Camadas do projeto

### Preparação

Padroniza nomes e tipos sem mudar o significado econômico da fonte.

### Intermediária

Agrega vendas e promoções na granularidade `produto × loja × semana` e cria a primeira regra de elegibilidade.

### Analítica

Combina venda, promoção e cadastro do produto. Inclui semanas promovidas sem venda observada, impedindo que ausência de transação seja confundida com ausência de exposição.

## Ponto crítico de senioridade

A tabela analítica ainda **não é automaticamente um painel causal**. Não existe estoque ou sortimento observado. Uma linha inexistente pode significar:

- venda zero;
- produto fora do sortimento;
- ruptura;
- loja não observada adequadamente.

Por isso, a elegibilidade inicial é explicitamente chamada de aproximação.

## Decisão de versão das ferramentas

O projeto usa a linha estável dbt Core 1.12 com DuckDB. O motor dbt v2/Fusion é mais recente, mas seu suporte local ao DuckDB ainda é beta. Trocar estabilidade por novidade não melhora a pergunta promocional; portanto, a migração para v2 fica como evolução futura, depois que o suporte amadurecer.

## Critério de saída

- todos os testes do dbt passaram;
- a chave `produto_id + loja_id + semana` é única;
- o número de semanas promovidas sem venda foi exibido;
- a quantidade de produtos sem categoria foi exibida;
- você sabe explicar por que a base não prova disponibilidade em estoque.

---

# Fase 4 — diagnóstico descritivo orientado à decisão

## Objetivo

Entender padrão, concentração e qualidade antes de estimar efeito.

## Análises obrigatórias

1. evolução semanal de unidades, vendas e descontos;
2. participação de cada mecânica promocional;
3. concentração das promoções por categoria, loja e produto;
4. distribuição de duração e repetição das promoções;
5. vendas em semanas promovidas e não promovidas, sem chamar a diferença de efeito;
6. proporção de promoção sem venda;
7. cobertura do cadastro de produtos;
8. mudança de composição entre períodos.

## Regra

Uma comparação bruta serve para diagnóstico, não para afirmação causal.

## Critério de saída

Cada tabela ou gráfico deve responder uma hipótese, revelar um risco ou alterar uma decisão posterior. Gráfico meramente decorativo é removido.

---

# Fase 5 — construir episódios promocionais

## Objetivo

Transformar semanas isoladas em eventos com início, fim e janelas de comparação.

## Definição inicial

- unidade: produto × loja;
- episódio: sequência contínua de semanas com uma mesma mecânica;
- janela anterior: 4 semanas;
- período promocional: duração observada do episódio;
- janela posterior: 4 semanas;
- intervalo mínimo entre episódios: suficiente para evitar sobreposição das janelas.

## Trade-off

Uma janela curta reduz contaminação por outros eventos, mas mede menos persistência. Uma janela longa capta antecipação melhor, porém aumenta sazonalidade e sobreposição.

## Critério de saída

- episódios possuem identificador único;
- janelas não se sobrepõem indevidamente;
- produtos sem histórico anterior suficiente são excluídos com motivo;
- a exclusão por elegibilidade é quantificada.

---

# Fase 6 — desenhar a comparação observacional

## Objetivo

Construir um grupo de comparação plausível para aproximar o cenário sem promoção.

## Estratégia principal proposta

Combinar:

- efeitos fixos de produto-loja, controlando características constantes da unidade;
- efeitos fixos de semana, controlando choques comuns;
- estudo de evento, mostrando semanas antes, durante e depois;
- pareamento ou ponderação como análise de sensibilidade, não como selo automático de causalidade.

## Verificações obrigatórias

- pré-tendências;
- sobreposição de características;
- ausência de tratamento simultâneo no grupo de comparação;
- concentração dos pesos;
- sensibilidade à janela;
- sensibilidade à regra de elegibilidade;
- erros-padrão agrupados na unidade compatível com o tratamento.

## Critério de saída

Se as pré-tendências divergirem materialmente, não force uma conclusão. Redesenhe o grupo, restrinja o universo ou classifique a evidência como inconclusiva.

---

# Fase 7 — estimar o efeito e a incerteza

## Resultados principais

- unidades adicionais estimadas;
- valor de venda adicional estimado;
- compradores adicionais estimados;
- intervalo de confiança;
- efeito relativo e absoluto;
- heterogeneidade por mecânica e categoria.

## O que não fazer

- apresentar apenas valor-p;
- esconder intervalo amplo;
- escolher somente a especificação com melhor resultado;
- chamar associação de “incremento causado” sem defender as premissas.

## Critério de saída

O resultado deve permanecer interpretável em unidades de negócio e conter incerteza, especificação principal e análises de robustez.

---

# Fase 8 — canibalização e antecipação

## Canibalização

Comparar o ganho do produto promovido com a mudança nos demais produtos da mesma categoria, priorizando substitutos plausíveis.

## Antecipação de compra

Verificar se o aumento durante a promoção é seguido por queda nas semanas posteriores.

## Métricas

```text
efeito líquido da categoria = efeito do produto promovido + efeito nos demais produtos
```

```text
efeito acumulado = efeito anterior + efeito durante + efeito posterior
```

## Critério de saída

A recomendação não pode usar apenas o pico durante a promoção.

---

# Fase 9 — cenários financeiros

## Limitação

A base não contém custo do produto, verba do fornecedor ou custo operacional da campanha.

## Solução correta

Apresentar cenários de margem, por exemplo 20%, 30% e 40%, e calcular o ponto de equilíbrio.

## O que não fazer

Não criar uma coluna de custo aleatória e apresentar “lucro real”.

## Critério de saída

A conclusão deve mostrar em quais premissas a decisão muda.

---

# Fase 10 — converter análise em decisão

| Evidência | Ação sugerida |
|---|---|
| efeito positivo, robusto, persistente e economicamente plausível | ampliar |
| efeito positivo apenas em grupos específicos | manter direcionado |
| volume sobe, mas valor líquido ou cenário econômico é fraco | redesenhar |
| efeito incerto ou sensível ao método | realizar experimento controlado |
| efeito desaparece após canibalização/antecipação | interromper |

Toda recomendação deve incluir: evidência, premissa, risco e próximo passo.

---

# Fase 11 — painel Power BI

## Página 1 — decisão executiva

- valor adicional estimado;
- unidades adicionais;
- intervalo de confiança;
- cenário econômico;
- recomendação por grupo.

## Página 2 — onde funciona

- mecânica;
- categoria;
- marca própria/nacional;
- loja ou agrupamento de lojas.

## Página 3 — riscos

- antecipação;
- canibalização;
- sensibilidade;
- cobertura e limitações.

## Página 4 — diagnóstico técnico

- pré-tendências;
- sobreposição;
- volume elegível;
- exclusões.

O painel não deve exigir que um diretor entenda regressão para tomar uma decisão.

---

# Fase 12 — publicar com credibilidade

## README final

Ordem recomendada:

1. problema;
2. decisão;
3. dados e limitações;
4. método;
5. resultados;
6. recomendação;
7. riscos;
8. como reproduzir.

## Linguagem

Use “efeito estimado sob as premissas do desenho observacional” quando apropriado. Não use “a promoção causou” apenas porque a regressão retornou significância.

---

# Fase 13 — defesa em entrevista

Você deve conseguir responder:

- por que não comparou diretamente semanas promovidas e não promovidas;
- por que resgate de cupom é comportamento posterior à exposição;
- como tratou venda zero, devolução e ausência de cadastro;
- por que escolheu produto × loja × semana;
- como avaliou pré-tendências;
- por que não inventou margem;
- quando recomendaria um experimento;
- qual decisão mudaria se a margem fosse menor;
- quais limitações impedem uma afirmação mais forte.

Consulte `documentacao/07_roteiro_entrevista.md`.
