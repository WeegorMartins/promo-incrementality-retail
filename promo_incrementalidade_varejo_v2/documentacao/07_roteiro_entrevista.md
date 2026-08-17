# Roteiro de defesa em entrevista

## Resumo em 60 segundos

> “O projeto avalia quais promoções de varejo geram venda adicional sustentável. Eu não comparei diretamente semanas promovidas e não promovidas porque produtos escolhidos para promoção podem ser estruturalmente diferentes. Modelei a unidade produto-loja-semana, preservei devoluções, incluí promoções sem venda e documentei que estoque não é observado. O desenho final combina estudo de evento e efeitos fixos, testa pré-tendências e mede canibalização e queda pós-promoção. Como a base não contém custos, uso cenários e ponto de equilíbrio em vez de inventar lucro.”

## Perguntas técnicas prováveis

### Por que produto × loja × semana?

Porque a exposição promocional é observada por produto, loja e semana. Agregar além disso perderia heterogeneidade; desagregar criaria precisão inexistente.

### Por que não usar quem resgatou cupom como tratado?

Porque resgate é uma escolha posterior e captura propensão prévia. A comparação misturaria efeito da campanha com perfil do consumidor.

### O que impede causalidade perfeita?

Seleção não aleatória da promoção, estoque não observado, concorrência ausente e possíveis choques específicos de produto-loja.

### Por que efeitos fixos?

Para controlar características constantes da combinação produto-loja e choques comuns de cada semana. Eles não resolvem confundidores que variam no tempo e afetam tratamento e resultado.

### Quando você recomendaria experimento?

Quando pré-tendências forem ruins, houver baixa sobreposição, resultado sensível à especificação ou decisão tiver alto impacto financeiro.

## Perguntas de negócio prováveis

### Vender mais basta?

Não. É necessário avaliar valor líquido, desconto, margem plausível, canibalização e antecipação.

### Qual promoção ampliar?

Somente a que apresentar efeito positivo robusto, persistência razoável e viabilidade em cenários econômicos plausíveis.

### O que fazer com resultado inconclusivo?

Não tratar como fracasso nem sucesso. Reduzir incerteza com teste controlado, universo menor ou coleta de estoque/custo.

