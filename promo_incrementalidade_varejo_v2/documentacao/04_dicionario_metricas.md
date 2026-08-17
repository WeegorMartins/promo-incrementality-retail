# Dicionário inicial de métricas

| Métrica | Fórmula | Granularidade | Uso | Limitação |
|---|---|---|---|---|
| unidades compradas | soma de quantidade em linhas positivas | produto × loja × semana | demanda bruta positiva | separa possíveis devoluções |
| unidades líquidas | soma de toda quantidade | produto × loja × semana | efeito líquido observado | pode misturar ajustes |
| valor de venda positivo | soma do valor em compras positivas | produto × loja × semana | valor recebido nas compras | não é margem |
| valor líquido | soma de todo valor de venda | produto × loja × semana | inclui ajustes negativos | exige diagnóstico |
| compradores | domicílios distintos em compra positiva | produto × loja × semana | alcance | painel de domicílios frequentes |
| cestas | cestas distintas em compra positiva | produto × loja × semana | frequência/ocasião | não representa todo o tráfego da loja |
| promoção registrada | exposição, encarte ou ambos | produto × loja × semana | tratamento observado | não garante disponibilidade |
| venda adicional estimada | observado menos contrafactual estimado | episódio/grupo | decisão | depende das premissas causais |
| canibalização | efeito nos demais itens da categoria | categoria × episódio | proteção | substitutos não são perfeitamente observados |
| antecipação | queda posterior relativa ao esperado | episódio | proteção | pode ser confundida com sazonalidade |

## Regra

Cada métrica final deverá ter fórmula, unidade, período, filtro, responsável e ressalva. Se duas áreas usam fórmulas diferentes, o painel não deve esconder a divergência.

