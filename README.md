# Sistema Preditivo de Falhas em Redes

## Objetivo
O projeto tem como objetivo desenvolver um sistema capaz de analisar dados de uma rede e usar essas informações para ajudar na previsão de possíveis falhas. Para isso, serão utilizadas informações relacionadas à latência, perda de pacotes e jitter, que serão organizadas e utilizadas como entrada para um modelo preditor.

## Descrição do projeto
O projeto consiste no desenvolvimento de um sistema para monitorar e analisar uma rede utilizando medições realizadas por meio do protocolo ICMP.
Os dados obtidos são organizados em registros e depois agrupados em janelas de medição. A partir dessas janelas, são obtidas as informações de latência, perda de pacotes e jitter, formando o vetor:`X = [latência, perda, jitter]`
Esse vetor será utilizado pelo modelo preditor para classificar a situação da rede e ajudar na identificação de possíveis condições de risco ou falha.
Durante o desenvolvimento do projeto, poderão ser utilizadas diferentes fontes de dados, como testes ativos com icmplib, datasets reais e a API do RIPE Atlas. A escolha da fonte dependerá da etapa do projeto, mantendo o mesmo formato de dados para utilização no modelo.

## Integrantes
- Breno Igor Ribeiro Da Silva
- Renata Mayumi Iuvata
- Ruan Abner Rodrigues Morales
- Isaque Ferreira de Jesus
- Lukas Paulo Alves de Carvalho
