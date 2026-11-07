# Sistema Preditivo de Falhas em Redes

## Objetivo

Construir um sistema de classificação de risco para redes, e não um notebook que roda uma vez. Ele lê medições periódicas de ping, prepara os dados, descreve cada fluxo em relação ao seu próprio comportamento normal e diz se o caminho está OK, em RISCO ou em FALHA. O trabalho também compara Árvore de Decisão, Random Forest e XGBoost para escolher o modelo mais adequado ao alerta.

O artigo completo do projeto está em `index.html`.

## Escopo

| Pergunta | Resposta |
|---|---|
| Qual evento será antecipado? | Degradação ou indisponibilidade de um fluxo de rede em relação ao baseline daquele fluxo. |
| Qual a delimitação de fluxos e caminhos? | Pares de probe de origem e endereço de destino: 5 Anchors do RIPE Atlas (Japão, Brasil, Canadá, Reino Unido e Austrália), com 4 probes por destino. Dos 19 fluxos que responderam, 16 têm baseline. O recorte junta caminhos curtos e longos, de 0,59 ms a 405,96 ms de mediana, para testar se o modelo separa distância de defeito. |
| Qual é o exato horizonte de previsão? | O modelo entregue é um detector do estado atual. Testamos também um preditor para 12 minutos à frente (±60 s), mas nenhum modelo superou a persistência em F1 macro e recall de FALHA ao mesmo tempo. |
| Qual a tolerância a Falsos Positivos versus Falsos Negativos? | Deixar uma FALHA passar custa mais, porque o enlace degrada sem investigação. A métrica principal é o F1 macro, sempre acompanhada do recall de FALHA. |
| Quem utilizará o alerta e qual ação ele engatilha? | Quem opera a rede (NOC, provedor ou campus). RISCO: observar e priorizar. FALHA: investigar perda, timeout ou desvio extremo. |
| Como será definida a classe? | Regra híbrida, auditável e relativa ao fluxo: desvio robusto do RTT, aumento relativo, jitter relativo, perda e persistência. |
| Quais dados estarão disponíveis no instante da predição? | Somente o passado do próprio fluxo: a ficha do Período A e até 5 medições recentes. |
| Qual fonte fornecerá o histórico completo? | API pública do RIPE Atlas, ping IPv4, em geral 3 pacotes por medição, uma medição a cada 240 s. Período A de 18/09 a 23/09/2026 e Período B de 24/09 a 29/09/2026, somando 74.960 medições. |

**Mudança registrada:** o memorando de 08/09/2026 recomendava o dataset da Hats Network. A coleta acabou sendo feita no RIPE Atlas, que entrega uma série contínua por fluxo, necessária para o baseline e para os dois períodos.

## Estrutura do repositório

```text
├── data/
│   ├── raw/          medições brutas, nunca editadas
│   └── processed/    baseline por fluxo, datasets e tabelas dos experimentos
├── src/              coleta.py, baseline.py e rotulo.py
├── notebooks/        coleta, Tarefas 2 a 6
├── models/           modelos .joblib, metadados e ficha do modelo
├── docs/             memorando, evidências e figuras do artigo
├── index.html        artigo do projeto
├── requirements.txt
└── README.md
```

## Como reproduzir

Instale as dependências (usamos Python 3.13):

```bash
pip install -r requirements.txt
```

Coleta. Pode rodar mais de uma vez, sem duplicar linhas:

```bash
python src/coleta.py
```

Baseline do Período A:

```bash
python src/baseline.py
```

Atributos, rótulos, recorte temporal e dataset do preditor:

```bash
python src/rotulo.py
```

Depois, abra os notebooks na ordem: `Tarefa3_Primeira_Arvore`, `Tarefa4_Ajuste_da_Arvore`, `Tarefa5_Arvore_Final` e `Tarefa6_Comparacao_Modelos`. As Tarefas 2 a 5 foram executadas no Google Colab e leem a pasta `ripe_atlas` do Drive. A Tarefa 6 também roda localmente, lendo `data/processed`.

Os scripts de `src/` foram conferidos contra os arquivos das tarefas: mesmas 74.960 medições, mesmo baseline, mesmas classes e mesmos blocos.

## Resultados

Detector, teste com folga, 10.150 medições:

| Modelo | F1 macro | Recall de FALHA | Erros |
|---|---:|---:|---:|
| Classe majoritária | 0,2967 | 0% | 2.009 |
| Árvore oficial (Tarefas 4 e 5) | 0,9993 | 99,71% | 3 |
| Árvore da busca (escolhida) | 0,9994 | 99,81% | 3 |
| Random Forest | 0,9994 | 99,81% | 3 |
| XGBoost | 0,9985 | 99,71% | 7 |



- Breno Igor Ribeiro Da Silva
- Renata Mayumi Iuvata
- Ruan Abner Rodrigues Morales
- Isaque Ferreira de Jesus
- Lukas Paulo Alves de Carvalho
