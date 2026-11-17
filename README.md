# Monitoramento Inteligente e Predição de Falhas em Redes

Projeto acadêmico desenvolvido na disciplina de **Estrutura de Dados II**, com coleta de medições reais de redes, análise em **Python** e aplicação de algoritmos de **Machine Learning** para classificar a condição de conexões e investigar a previsão de falhas futuras.

🌐 **[Acesse o site do projeto](https://redswann.github.io/sistema-preditivo-de-falhas-em-redes/)**

## 1. Visão geral

O projeto analisa medições periódicas de conectividade para identificar se um fluxo de rede está em uma das três condições:

- **OK:** comportamento compatível com a condição normal do fluxo;
- **RISCO:** sinais de degradação ou instabilidade;
- **FALHA:** condições mais graves, como perda de pacotes, ausência de resposta ou desvios relevantes.

O trabalho contempla **dois problemas distintos**:

1. **Detecção do estado atual:** classificar uma medição como OK, RISCO ou FALHA. A **Árvore de Decisão** das Tarefas 4 e 5 é o modelo oficial dessa etapa.
2. **Predição do estado futuro:** estimar a classe da rede aproximadamente **20 minutos à frente**, com tolerância de **±60 segundos**, a partir das informações disponíveis no instante atual. Essa avaliação é realizada separadamente na Tarefa 6 e permanece **experimental**.

> **Importante:** o projeto implementa e avalia a predição futura em dados históricos, mas não demonstra um serviço de alertas em operação contínua e em tempo real.

## 2. Tecnologias utilizadas

| Tecnologia | Aplicação no projeto |
|---|---|
| **Python 3.13** | Coleta, preparação, rotulagem, treinamento e avaliação |
| **RIPE Atlas (API pública)** | Fonte de medições reais de conectividade |
| **Pandas e NumPy** | Tratamento de tabelas e cálculos estatísticos |
| **Scikit-learn** | Árvore de Decisão, Random Forest, preparação e métricas |
| **XGBoost** | Modelo adicional de comparação |
| **Matplotlib** | Gráficos e visualização das árvores |
| **Joblib** | Persistência de modelos treinados |
| **Jupyter / Google Colab** | Execução e documentação dos experimentos |
| **GitHub / GitHub Pages** | Versionamento e publicação do site |

As versões declaradas das principais dependências estão em [`requirements.txt`](requirements.txt).

## 3. Origem e características dos dados

As medições foram obtidas por meio da **API do RIPE Atlas**, utilizando testes de **ping IPv4**. A coleta considera cinco destinos associados a Anchors do RIPE Atlas — **Japão, Brasil, Canadá, Reino Unido e Austrália** — e probes de origem selecionadas.

O recorte documentado considera:

- **Período A:** 18 a 23 de setembro de 2026, usado para estabelecer o comportamento de referência (*baseline*) de cada fluxo;
- **Período B:** 24 a 29 de setembro de 2026, usado para classificação e experimentos;
- **74.960 medições** no conjunto consolidado descrito na coleta;
- **19 fluxos com resposta**, dos quais **16** dispõem de baseline suficiente, conforme o recorte documentado.

A coleta registra medições com intervalos tipicamente próximos de **240 segundos** e, em geral, três pacotes por medição. Os resultados podem variar conforme a disponibilidade das probes e dos fluxos.

### Indicadores analisados

| Indicador | Significado |
|---|---|
| **RTT** | Tempo de ida e volta de um pacote entre origem e destino |
| **Jitter** | Variação dos tempos de resposta, estimada a partir das respostas da medição |
| **Perda de pacotes** | Proporção de pacotes enviados sem resposta |
| **Timeout** | Medição sem resposta dentro do prazo esperado |
| **Baseline** | Referência histórica do comportamento normal de cada fluxo |
| **Z robusto** | Desvio do RTT em relação ao baseline, usando mediana e MAD |

O baseline é calculado com o **Período A**, sem incorporar as medições do Período B. Assim, o modelo considera o comportamento próprio de cada fluxo, evitando tratar automaticamente um caminho longo como defeituoso apenas por ter RTT maior.

## 4. Preparação, atributos e rotulagem

Os dados brutos são padronizados, agrupados por fluxo e transformados em atributos para os modelos. As classes **OK**, **RISCO** e **FALHA** são produzidas por uma política de rotulagem baseada nas métricas da rede e em ocorrências recentes.

As **oito variáveis utilizadas pelos modelos** são:

| Variável | O que representa |
|---|---|
| `z_robusto` | Desvio robusto do RTT em relação ao baseline |
| `aumento_pct` | Aumento relativo do RTT |
| `jitter_relativo` | Variação do RTT em relação à referência do fluxo |
| `perda_pct` | Percentual de perda de pacotes |
| `timeout_atual` | Indicação de timeout na medição atual |
| `n5_timeout` | Ocorrências de timeout nas últimas cinco medições |
| `n5_aumento80` | Ocorrências recentes de aumento elevado do RTT |
| `n5_risco` | Ocorrências recentes de condição de risco |

Identificadores de fluxo, endereços IP, país, timestamps e o RTT absoluto **não são utilizados como entradas do modelo oficial**. As janelas históricas são construídas a partir de informações disponíveis até o instante analisado.

### Alvos de classificação

- **Detector:** `status_atual` / `classe`, conforme o dataset utilizado em cada notebook.
- **Preditor:** `status_futuro`, obtido pelo pareamento temporal de medições do mesmo fluxo perto de **t + 20 minutos (±60 s)**.

No pareamento futuro, registros sem correspondência dentro da tolerância ou com alvo pertencente a outro bloco temporal são descartados. A previsão por **persistência** repete a classe atual e serve como referência para comparação.

## 5. Etapas dos notebooks

| Notebook | Responsabilidade |
|---|---|
| `Coleta_dados_brutos.ipynb` | Consulta ao RIPE Atlas e consolidação das medições |
| `Tarefa2_Baseline_Rotulagem.ipynb` | Baseline, atributos, regras de rotulagem, recorte temporal e datasets do detector e do preditor |
| `Tarefa3_Primeira_Arvore.ipynb` | Treinamento inicial e busca de hiperparâmetros da Árvore de Decisão |
| `Tarefa4_Ajuste_da_Arvore.ipynb` | Análise de erros, ajuste e congelamento da configuração da árvore |
| `Tarefa5_Arvore_Final.ipynb` | Teste temporal oficial, matriz de confusão, métricas e exportação do modelo |
| `Tarefa6_Comparacao_Modelos.ipynb` | Comparação com Random Forest e XGBoost; experimento separado de predição futura |

### Árvore de Decisão oficial

A configuração selecionada nas Tarefas 3 e 4 e avaliada na Tarefa 5 utiliza:

```python
DecisionTreeClassifier(
    criterion="entropy",
    max_depth=5,
    min_samples_leaf=10,
    random_state=42,
)
```

A árvore treinada possui **19 folhas**. Os hiperparâmetros foram selecionados na validação, sem utilizar o conjunto de teste para escolher a configuração final.

## 6. Resultados experimentais

### 6.1. Detector do estado atual — teste oficial da Tarefa 5

A avaliação temporal oficial foi realizada com **3.417 registros** do período de teste.

| Indicador | Resultado |
|---|---:|
| **F1 macro** | **0,9978** |
| Acurácia | 99,9122% |
| Recall de FALHA | 99,68% |
| Erros | **3** |
| Total de registros | **3.417** |

**Matriz de confusão** (linhas = classe real; colunas = classe prevista):

| Classe real | OK | RISCO | FALHA |
|---|---:|---:|---:|
| **OK** | 2.788 | 0 | 0 |
| **RISCO** | 2 | 315 | 0 |
| **FALHA** | 0 | 1 | 311 |

A árvore classificou corretamente **311 de 312** ocorrências rotuladas como FALHA. Os três erros foram dois casos de **RISCO classificados como OK** e um caso de **FALHA classificado como RISCO**.

> **Interpretação:** como os rótulos foram definidos por regras que utilizam métricas semelhantes às entradas da árvore, o desempenho elevado indica principalmente a capacidade de **reproduzir a política de rotulagem**. Não é, por si só, uma demonstração de antecipação de falhas futuras reais.

### 6.2. Comparação entre modelos — Tarefa 6

A Tarefa 6 realiza uma comparação adicional do **detector atual** com recorte temporal e folga, em **3.337 registros**. Esse conjunto **não é o mesmo** teste de 3.417 registros da Tarefa 5.

| Modelo | F1 macro | Recall de FALHA | Erros |
|---|---:|---:|---:|
| Classe majoritária | 0,2994 | 0,00% | 617 |
| Árvore de Decisão | 0,9977 | 99,67% | 3 |
| Random Forest | 0,9989 | 99,67% | 1 |
| XGBoost | 0,9988 | 100,00% | 2 |

Embora outros modelos apresentem resultados ligeiramente superiores em alguns indicadores, a **Árvore de Decisão** foi mantida como modelo oficial pela combinação de desempenho, simplicidade e interpretabilidade, conforme a seleção documentada na validação.

### 6.3. Predição futura — aproximadamente 20 minutos

A Tarefa 6 também avalia um problema diferente: prever a classe futura a partir das oito variáveis disponíveis no instante atual. O teste desse experimento contém **3.228 registros**.

| Modelo | F1 macro | Recall de FALHA | Erros |
|---|---:|---:|---:|
| Classe majoritária | 0,2989 | 0,00% | 605 |
| **Persistência** | **0,7754** | **69,57%** | **351** |
| Árvore de Decisão | 0,8308 | 67,89% | 242 |
| Random Forest | **0,8330** | 68,23% | **238** |
| XGBoost | 0,8292 | 68,56% | 246 |

Os três modelos de Machine Learning superaram a persistência em **F1 macro** e reduziram a quantidade total de erros. Entretanto, **nenhum superou a persistência no recall da classe FALHA**. Por isso, a previsão futura está implementada e avaliada, mas ainda não é considerada suficientemente confiável para alertas operacionais antecipados.

## 7. Estrutura do repositório

```text
├── data/
│   ├── raw/             # Medições originais e consolidadas
│   ├── interim/         # Arquivos intermediários e auditorias
│   └── processed/       # Baselines e datasets preparados
├── src/
│   ├── coleta.py        # Consulta e consolidação de medições
│   ├── baseline.py      # Preparação e referência por fluxo
│   └── rotulo.py        # Atributos, classes e alvo futuro
├── notebooks/           # Coleta e Tarefas 2 a 6
├── models/              # Modelos e metadados exportados
├── entrega_final/       # Artefatos da entrega acadêmica
├── docs/                # Documentação, figuras e evidências
├── index.html           # Site do projeto
├── requirements.txt     # Dependências Python
└── README.md
```

## 8. Como reproduzir

### Requisitos

- Python 3.13 e dependências do projeto;
- Acesso aos arquivos de dados e aos notebooks;
- Para os notebooks executados no Colab, acesso à pasta `ripe_atlas` no Google Drive, conforme os caminhos definidos nas células.

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Os scripts do repositório podem ser executados nesta sequência:

```bash
python src/coleta.py
python src/baseline.py
python src/rotulo.py
```

**Atenção — divergência conhecida:** na versão de `src/rotulo.py` examinada, o horizonte está definido como `HORIZONTE_S = 12 * 60`, enquanto o notebook **Tarefa 2** revisado utiliza `HORIZONTE_SEGUNDOS = 20 * 60`. Portanto, **executar o script atual não reproduz exatamente o dataset de predição futura dos notebooks**. Antes de utilizá-lo para reproduzir os resultados de 20 minutos, é necessário alinhar o código do script e verificar novamente suas saídas.

Para reproduzir os experimentos documentados, utilize os **notebooks revisados**, seguindo a sequência das Tarefas 2 a 6 e verificando os caminhos de entrada e os artefatos exigidos por cada etapa. A Tarefa 5 depende do modelo produzido na Tarefa 4; a Tarefa 6 utiliza a árvore oficial e os datasets preparados.

A simples execução dos comandos acima **não garante** reproduzir todos os resultados dos notebooks sem conferir versões, arquivos de entrada, recortes e configurações.

## 9. Limitações e próximos passos

- As classes são derivadas de **regras de rotulagem**, não de chamados reais de incidentes de rede; por isso, os resultados do detector não devem ser interpretados como validação independente de falhas reais.
- O baseline do Período A é fixo e pode não acompanhar mudanças de rota ou de comportamento ao longo do tempo.
- Rajadas curtas de ping podem limitar a qualidade da estimativa do jitter.
- As medições do RIPE Atlas não representam diretamente a rede de um campus ou provedor específico.
- A predição futura ainda precisa melhorar a **identificação antecipada da classe FALHA**, especialmente em comparação com a persistência.
- A operação em tempo real, com coleta contínua, inferência automática e emissão de alertas, é uma **possibilidade de evolução**, não uma funcionalidade demonstrada nesta entrega.

## 10. Integrantes

- Breno Igor Ribeiro Da Silva
- Renata Mayumi Iuvata
- Ruan Abner Rodrigues Morales
- Isaque Ferreira de Jesus
- Lukas Paulo Alves de Carvalho

---

**Projeto acadêmico — Estrutura de Dados II | 2026**
