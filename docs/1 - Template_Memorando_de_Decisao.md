# Memorando de Decisão — Fonte de Dados do Projeto


| Campo | Informação |
|---|---|
| Curso / Disciplina | `[Estrutura de Dados 2]` |
| Projeto integrador | `[]` |
| Orientador(a) | `[Andrea Ono Sakai]` |
| Data de entrega desta etapa | `[]` |
| Integrantes do grupo | `[Renata Mayumi Iuvata, Ruan Abner Rodrigues Morales, isaque farreira de jesus, lukas paulo alves de carvalho]` |

---

> Preencha cada seção com o que você encontrou na pesquisa. Não deixe nenhum campo com o texto entre colchetes — substitua pelo seu conteúdo. Toda informação levantada nas Opções A e B precisa indicar a fonte de onde veio.

## 1. Situação

<!-- Em uma frase: qual decisão precisa ser tomada e por quê. 
O pipeline do projeto já está definido: qualquer fonte de dados precisa produzir registros que se transformem em janelas e, por fim, em X = [latência, perda, jitter]. Falta decidir de onde virão esses dados na próxima fase. A equipe do projeto precisa recomendar, com base em pesquisa e não em preferência pessoal, se a próxima etapa deve usar um dataset real já publicado ou a API do RIPE Atlas. O grupo deve produzir um memorando de decisão com a recomendação da tomada de decisão. A recomendação só tem valor se for sustentada por pesquisa real — não existe resposta pronta para copiar; ela precisa ser construída a partir do que vocês encontraram.
-->

A equipe precisa decidir se, na próxima etapa do projeto, será usado um dataset real já publicado ou dados coletados pela API do RIPE Atlas, porque é necessário definir uma fonte de dados adequada que permita gerar registros, transformá-los em janelas e obter as métricas de latência, perda de pacotes e jitter utilizadas pelo projeto.

## 2. Opção A — Dataset real

<!-- O que foi encontrado sobre um dataset real de ICMP. Cite a fonte de cada informação. -->

- **Origem / link:** [Hats Network - Global Network Latency Dataset. É um dataset público que contém medições reais de latência de rede feitas entre pontos de presença.]
- **Formato:** [Os arquivos são disponibilizados em formato .csv, podendo ser uma matriz geral contendo um agregado das medições analisadas na rodada ou um arquivo contendo medições individuais de cada pacote.]
- **Período coberto:** [Esse dataset é organizado em rodadas de medição nomeadas como timestamp. Cada rodada tem 50 medições, analisadas ao longo de 4,9 segundos, com um intervalo de 100 ms entre elas.]
- **Campos disponíveis:** [
  No arquivo individual, estão disponíveis os campos:

  round_id: identifica quando o teste foi realizado; 
  seq: identifica a ordem de cada teste;
  offset_ms: informa quanto tempo passou desde o início do teste;
  rtt_ms: informa o tempo de resposta de ida e volta da comunicação em milissegundos.
  ]
- **Licença de uso:** [Os dados podem ser utilizados e adaptados desde que sejam atribuídos os devidos créditos à fonte original, de acordo com os termos de licença.]

**Resumo do que foi encontrado:**

  O Hats Network - Global Network Latency Dataset é um dataset que reúne medições de latência realizadas entre diferentes pontos de presença. Os dados são obtidos por meio de testes de rede e disponibilizados em arquivos .csv.
  O dataset apresenta duas formas diferentes de dados: uma matriz geral, que unifica as informações das medições realizadas em uma rodada, e arquivos individuais, que apresentam os resultados de cada pacote enviado durante os testes.
  Cada rodada possui 50 medições, realizadas em intervalos de 100 ms.
  Nos arquivos são disponibilizadas informações como o momento em que o teste foi realizado (round_id), a ordem de cada pacote (seq) e o intervalo de tempo desde o início do teste (offset_ms), além do tempo de ida e volta da comunicação (rtt_ms).
  A partir dessas medições, os dados podem ser processados e organizados para obter características como latência, perda de pacotes e jitter.

  Fonte: hatsnet.io/opendata



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
| Controle sobre a coleta | Nenhum. As medições já foram realizadas e seus parâmetros foram definidos anteriormente. | Parcial. Alguns parâmetros podem ser definidos, como o destino, os pontos de medição e a frequência dos testes. |
| Diversidade geográfica | Varia de acordo com os locais abrangidos pelo dataset e com a forma como os dados foram coletados. | Alta, devido à distribuição dos pontos de medição em diferentes países e redes. |
| Custo / complexidade de implementação | Baixo. Os arquivos já estão disponíveis, sendo necessário apenas obtê-los e organizar os dados para utilizá-los no projeto. | Médio. A utilização envolve a integração com a API, o uso de uma API Key para criar medições e a consulta dos resultados. |
| Tempo até os primeiros dados estarem disponíveis | Imediato, pois as medições já foram realizadas e os dados estão disponíveis para acesso e tratamento. | Após alguns minutos, considerando o tempo necessário para criar e executar a medição antes de consultar os resultados. |

## 5. Recomendação

<!-- Uma frase direta: qual opção você recomenda. -->

Recomenda-se o uso da API do RIPE Atlas como fonte de dados para a próxima etapa do projeto, pois ela proporciona maior controle sobre a coleta de informações, oferece uma maior diversidade geográfica e permite configurar as medições conforme as necessidades específicas do pipeline.

## 6. Justificativa

<!-- Por que essa opção vence a outra, com base nas evidências das seções 2, 3 e 4 — não em preferência pessoal. -->

A escolha da API do RIPE Atlas é justificada pelo maior controle e flexibilidade durante a coleta de dados. Ao contrário do dataset real, que já foi coletado e não pode ser modificado, a API permite definir detalhes como o destino, os probes utilizados e a frequência das medições.

Além disso, os probes estão distribuídos por várias regiões e redes, o que traz mais diversidade geográfica. Isso facilita a adaptação da coleta de dados às necessidades do projeto e ao pipeline responsável por gerar as métricas de latência, perda de pacotes e jitter.

Mesmo que a API tenha uma implementação mais complexa e demande mais tempo para executar as medições, essas dificuldades são compensadas pelo fato de poder coletar dados personalizados e alinhados aos objetivos do projeto. Por isso, considerando as duas opções, a API do RIPE Atlas é a escolha mais apropriada para a próxima etapa.

## 7. Riscos e limitações

<!-- O que pode dar errado com a opção escolhida, e como isso poderia ser mitigado -->.

A utilização da API do RIPE Atlas traz alguns riscos e limitações que precisam ser levados em conta durante a execução do projeto. Um dos principais riscos está relacionado à necessidade de uma API Key para criar medições. Se a chave não tiver as permissões adequadas, a criação das medições pode falhar. Para minimizar esse problema, é importante configurar a chave corretamente e realizar testes de autenticação antes de iniciar a execução definitiva.

Outro ponto importante é que os resultados não ficam disponíveis imediatamente após a criação da medição. É necessário criar a Measurement, esperar que ela seja executada e só então acessar os dados. Esse atraso pode impactar o tempo de processamento dos dados se a equipe não considerar esse tempo no planejamento. A melhor forma de mitigar isso é criar as medições com antecedência e verificar o status das medições antes de coletar os resultados.

Também há uma limitação relacionada à disponibilidade e à seleção dos probes. Embora o RIPE Atlas tenha uma ampla distribuição geográfica, a quantidade e a localização dos probes disponíveis podem variar dependendo dos critérios escolhidos. Para reduzir esse impacto, é essencial selecionar um número suficiente de probes e garantir que eles estejam bem distribuídos na região que será analisada.

Por fim, usar a API do RIPE Atlas aumenta a complexidade em comparação com o uso de um dataset pronto. É preciso integrar a API, criar as medições e depois consultar os resultados. Para reduzir esse risco, a equipe deve começar com uma medição de teste e confirmar se os dados obtidos podem ser convertidos corretamente nas janelas que o pipeline do projeto precisa.

Assim, os principais riscos envolvem autenticação, tempo de execução das medições, disponibilidade dos probes e a complexidade da integração. Esses riscos podem ser mitigados com testes antecipados, planejamento cuidadoso da coleta e validação dos dados antes de usá-los de forma definitiva no projeto.

## 8. Contribuição Individual dos Integrantes

<!-- cada integrante deve descrever, com suas próprias palavras, o que efetivamente fez nesta etapa. Contribuições genéricas como "ajudei em tudo" não serão aceitas. Use verbos de ação e seja específico (ex.: "pesquisei , analisei, testei, ... apresentei prós/contras ao grupo, ...").-->

### Integrante 1 — `[isaque ferreira de jesus ]`
- **O que fez nesta etapa:** `[etapa 1 e 7]`
- **Tempo dedicado (aprox.):** `[ex.: 1h00]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
`[]` 
`[]`

### Integrante 2 — `[lukas paulo Alves de carvalho ]`
- **O que fez nesta etapa:** `[recomendei a API d RIPE atlas como a melhor opção e justifiquei a minha opnião, etapa 5 e 6]`
- **Tempo dedicado (aprox.):** `[ex.: 1h15]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
`[]` 
`[]`

### Integrante 3 — `[Ruan Abner Rodrigues Morales ]`
- **O que fez nesta etapa:** `[3. Opção B — API do RIPE Atlas]`
- **Tempo dedicado (aprox.):** `[3h00]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

### Integrante 4 — `[ Breno Igor Ribeiro Da Silva ]`
- **O que fez nesta etapa:** `[2. Opcao A - pesquisa sobre funcionamento e para encontrar datasets reais]`
- **Tempo dedicado (aprox.):** `[2h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

### Integrante 5 — `[Renata Mayumi Iuvata ]`
- **O que fez nesta etapa:** `[A seção de comparação]`
- **Tempo dedicado (aprox.):** `[1h10]`
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

1. [ hatsnet.io/opendata ]
2. [ ]
3. [ ]
