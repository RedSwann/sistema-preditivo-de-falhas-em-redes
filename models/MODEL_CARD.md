# Ficha do modelo

## O que é

Detector do estado atual de um fluxo de rede: classifica uma medição de ping em OK, RISCO ou FALHA pelo desvio em relação ao baseline do próprio fluxo. **Não prevê o futuro.** No teste de 12 minutos à frente, nenhum modelo superou a persistência em F1 macro e recall de FALHA ao mesmo tempo.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `modelo.joblib` | **Modelo entregue** em 04/11/2026 (versão 1.0.0): a árvore oficial da Tarefa 5. Dicionário com `modelo`, `features`, `familia` e `params`. A predição devolve o nome da classe. |
| `metadados.json` | Fórmulas, exceções, ambiente e métricas da árvore oficial, na versão enviada. |
| `modelo_tarefa6.joblib` | Árvore escolhida na comparação da Tarefa 6, feita depois da entrega. Não substitui o modelo entregue. Dicionário com `modelo`, `features`, `classes_codificadas`, `limiar`, `params` e `nome`. A predição devolve o índice da classe em `classes_codificadas`. |

Só abra um arquivo `.joblib` de fonte em que você confia, porque ele pode executar código ao ser carregado. Os dois exigem scikit-learn 1.6.1.

## Parâmetros

| | Árvore oficial | Árvore da Tarefa 6 |
|---|---|---|
| Critério | Gini | Entropia |
| `max_depth` | 4 | 6 |
| `min_samples_leaf` | 10 | 10 |
| Peso por classe | Não | Sim (`balanced`) |
| Folhas | 11 | 11 |
| Semente | 42 | 42 |

Os dois usam `SimpleImputer(strategy="median")` dentro de um `Pipeline`.

## Entradas

Oito colunas, nesta ordem: `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco`.

País, IP, rota, `fluxo_id` e RTT absoluto não entram.

## Dados

RIPE Atlas, ping IPv4, 16 fluxos com baseline. Baseline no Período A (18/09 a 23/09/2026), com pelo menos 1.500 RTTs válidos. Treino, validação e teste em ordem de tempo dentro do Período B (24/09 a 29/09/2026): 17.028, 6.806 e 10.230 medições.

## Desempenho

| Teste | Modelo | F1 macro | Recall de FALHA | Erros |
|---|---|---:|---:|---:|
| Tarefa 5, sem folga (10.230) | Árvore oficial | 0,9991 | 99,62% | 4 |
| Tarefa 6, com folga (10.150) | Árvore oficial | 0,9993 | 99,71% | 3 |
| Tarefa 6, com folga (10.150) | Árvore da Tarefa 6 | 0,9994 | 99,81% | 3 |
| Fluxos nunca vistos (10.150) | Árvore oficial | 0,9969 | 99,24% | 14 |
| Fluxos nunca vistos (10.150) | Árvore da Tarefa 6 | 0,9981 | 99,24% | 8 |

## O que ele não faz

- Não detecta falha confirmada em equipamento. Ele reproduz uma política de rótulo feita com as mesmas métricas que lê, por isso os valores ficam perto de 100%.
- Não opera em fluxo sem ficha. Para um fluxo novo, é preciso observar um período inicial, congelar a ficha e só então aplicar os atributos.
- Não distingue troca de rota de degradação. Com o baseline fixo, 25,2% das FALHA e 40,5% das RISCO estão em janelas com sinal de troca de rota.

Os resultados são estimativas experimentais e não substituem a análise de quem opera a rede.
