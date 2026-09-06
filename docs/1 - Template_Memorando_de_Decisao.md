# Memorando de Decisão — Fonte de Dados do Projeto


| Campo | Informação |
|---|---|
| Curso / Disciplina | `[]` |
| Projeto integrador | `[]` |
| Orientador(a) | `[]` |
| Data de entrega desta etapa | `[]` |
| Integrantes do grupo | `[]` |

---

> Preencha cada seção com o que você encontrou na pesquisa. Não deixe nenhum campo com o texto entre colchetes — substitua pelo seu conteúdo. Toda informação levantada nas Opções A e B precisa indicar a fonte de onde veio.

## 1. Situação

<!-- Em uma frase: qual decisão precisa ser tomada e por quê. 
O pipeline do projeto já está definido: qualquer fonte de dados precisa produzir registros que se transformem em janelas e, por fim, em X = [latência, perda, jitter]. Falta decidir de onde virão esses dados na próxima fase. A equipe do projeto precisa recomendar, com base em pesquisa e não em preferência pessoal, se a próxima etapa deve usar um dataset real já publicado ou a API do RIPE Atlas. O grupo deve produzir um memorando de decisão com a recomendação da tomada de decisão. A recomendação só tem valor se for sustentada por pesquisa real — não existe resposta pronta para copiar; ela precisa ser construída a partir do que vocês encontraram.
-->

[Escreva aqui uma frase, qual decisão precisa ser tomada e por quê]

## 2. Opção A — Dataset real

<!-- O que foi encontrado sobre um dataset real de ICMP. Cite a fonte de cada informação. -->

- **Origem / link:** [ ]
- **Formato:** [ ]
- **Período coberto:** [ ]
- **Campos disponíveis:** [ ]
- **Licença de uso:** [ ]

**Resumo do que foi encontrado:**

[Escreva aqui, citando a fonte consultada]

## 3. Opção B — API do RIPE Atlas

<!-- O que foi encontrado sobre a API: autenticação, criação e consulta de medições. Cite a fonte de cada informação. -->

- **Documentação consultada (link):** [https://atlas.ripe.net/docs/apis/rest-api-manual/ ]
- **Autenticação exigida:** [Para criar uma medição, é necessário utilizar uma API Key com a permissão necessária para criação de medições. A chave deve ser enviada no cabeçalho HTTP Authorization, utilizando o formato Authorization: Key SUA_API_KEY. A documentação informa que a API Key é o método preferencial para acesso programático]
- **Como se cria uma medição:** [
Uma medição possui informações relacionadas a:  
identificação;  
tipo de teste;  
destino;  
probes utilizados;  
configuração;  
frequência;  
horário de início;  
horário de término;  
estado da medição;  
resultados.  

O RIPE atlas permite criar diferentes tipos de testes:

| Tipo           | Descrição                                        |
| -------------- | ------------------------------------------------ |
| **Ping**       | Mede a comunicação e a latência até um destino   |
| **Traceroute** | Identifica o caminho percorrido pelos pacotes    |
| **DNS**        | Realiza consultas DNS                            |
| **SSL/TLS**    | Obtém informações do certificado TLS/SSL         |
| **HTTP**       | Realiza requisições HTTP                         |
| **NTP**        | Verifica sincronização de horário através do NTP |
 
Será necessário três componentes principais:
1. Definition - O que será medido;
2. Probe selection — de onde a medição será realizada;
3. Timing/global fields — quando e como a medição será executada;

O campo definitions contém as definições das medições que serão criadas.  
Cada definição precisa informar, no mínimo: 

description - Identifica a medição para o usuário: "description": "Ping no RIPE"  
type - Define o tipo de teste: "type": "ping"  
af - Define a família de endereços utilizada: 4 → IPv4 6 → IPv6  
target - Define o destino do teste: "target": "ripe.net"  

Seleção dos Probes:  
Os probes são os dispositivos responsáveis por executar as medições.  

A seleção é realizada através do campo:  

"probes": []

A documentação permite selecionar probes de diferentes maneiras, incluindo região, país, ASN, IDs específicos e outras formas de seleção.  
Exemplo por região:  
{  
  "requested": 10,  
  "type": "region",  
  "value": "south_america"  
}  

Configurando a frequência:  
Em uma medição recorrente, podemos definir o intervalo entre os testes através de:  

"interval": 1800  

O valor é expresso em segundos.  

60= 1 minuto;  
300= 5 minutos;  
600= 10 minutos;  
1800= 30 minutos;  
3600= 1 hora; 

Exemplo completo com Ping:  
Um exemplo simples de criação de uma medição seria:  

curl --location 'https://atlas.ripe.net/api/v2/measurements/' \  
--header 'Authorization: Key SUA_API_KEY' \  
--header 'Content-Type: application/json' \  
--data '{  
  "definitions":   [
    {
      "target": "ripe.net",  
      "description": "Teste de Ping",  
      "type": "ping",  
      "af": 4  
    }  
  ],  
  "probes": [  
    {  
      "requested": 5,  
      "type": "region",  
      "value": "south_america"  
    }  
  ]  
}'  
  
Quando a criação ocorre com sucesso, a API retorna os identificadores das medições criadas.
Exemplo:

{
  "measurements": [
    12345678
  ]
}

O número ID da Measurement:

12345678

Esse ID é importante porque será utilizado posteriormente para consultar informações e resultados da medição.
Depois de criada, uma medição pode ser consultada através de: GET /api/v2/measurements/{id}/
Por exemplo: GET https://atlas.ripe.net/api/v2/measurements/12345678/

A resposta pode conter informações como:
ID
tipo
destino
status
probes
intervalo
horários
descrição
configurações
]

- **Como se consultam os resultados:** 
[Depois que a medição for executada, seus resultados podem ser consultados através dos endpoints de resultados associados à Measurement.

A lógica geral é:  
1. Criar Measurement  
2. Receber Measurement ID  
3. Aguardar execução  
4. Consultar resultados  
5. Analisar os dados

Por exemplo:

Measurement ID  
      │  
      ↓  
12345678  
      │  
      ↓  
Resultados  
      │  
      ├── Probe 101 → 20 ms  
      ├── Probe 205 → 25 ms  
      ├── Probe 310 → 31 ms  
      └── Probe 415 → 42 ms]  
      
**Resumo do que foi encontrado:**

[A REST API do RIPE Atlas permite criar e consultar medições de rede realizadas por probes distribuídos pela Internet. Para criar uma medição, é necessário utilizar uma API Key com a permissão adequada e enviar uma requisição POST para o endpoint de medições. A requisição deve informar o tipo de teste que será realizado, o destino e quais probes serão utilizados. Depois da criação, a API retorna um identificador da medição, que pode ser utilizado para consultar seus resultados através de requisições GET. A documentação também informa que, enquanto a criação de medições exige autenticação, várias operações de consulta de dados públicos podem ser realizadas sem autenticação.

Fonte: https://atlas.ripe.net/docs/apis/rest-api-manual/
]

## 4. Comparação

<!-- Preencha a tabela com base no que você levantou nas seções 2 e 3. -->

| Critério | Opção A — Dataset real | Opção B — API RIPE Atlas |
|---|---|---|
| Controle sobre a coleta | | |
| Diversidade geográfica | | |
| Custo / complexidade de implementação | | |
| Tempo até os primeiros dados estarem disponíveis | | |

## 5. Recomendação

<!-- Uma frase direta: qual opção você recomenda. -->

[Escreva aqui]

## 6. Justificativa

<!-- Por que essa opção vence a outra, com base nas evidências das seções 2, 3 e 4 — não em preferência pessoal. -->

[Escreva aqui]

## 7. Riscos e limitações

<!-- O que pode dar errado com a opção escolhida, e como isso poderia ser mitigado. -->

[Escreva aqui]

## 8. Contribuição Individual dos Integrantes

<!-- cada integrante deve descrever, com suas próprias palavras, o que efetivamente fez nesta etapa. Contribuições genéricas como "ajudei em tudo" não serão aceitas. Use verbos de ação e seja específico (ex.: "pesquisei , analisei, testei, ... apresentei prós/contras ao grupo, ...").-->

### Integrante 1 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
`[]` 
`[]`

### Integrante 2 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
`[]` 
`[]`

### Integrante 3 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

### Integrante 4 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

### Integrante 5 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

### Integrante 6 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

---

## Fontes consultadas

<!-- Mínimo de 3 fontes. Liste todas as páginas de documentação, artigos ou repositórios usados. -->

1. [ ]
2. [ ]
3. [ ]
