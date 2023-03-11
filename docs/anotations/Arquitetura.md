# Arquitetura IoT

## Equipamentos que serão utilizados
| Nome  | Quantidade | Código Fonte |
|-------|------------|-------|
|Sensor de Temperatura e Umidade|N |        |
|Modulo de Captura| 1  |        |
|Modulo de Controle| 1 |       |


## Definição da Arquitetura

Questionamentos a serem respondidos pela arquitetura.

- Quem fará o processamento das informações de Temperatura e Umidade?
- Quem fará o processamento das Imagens?
- Com quem o Sensor de Temperatura e Umidade se comunicará?
- Com quem o Modulo de Captura se comunicará?

Tendo em vista a computação de borda, ou seja, o equipamento que adquire o dado já o processa faz sentido optarmos por uma arquitetura a qual o modulo de controle funcione apenas como uma visualização das decisões tomadas. Porém, dois fatores corroboram com o processamento das informações de temperatura e umidade serem realizados dentro do módulo de controle:

 - Barateio dos Sensores de Temperatura e Umidade (o que permite o custo do sistema um projeto de baixo custo em largas areas).

 - Possibilidade de analise de dados (temperatura e umidade) em conjunto.
 
 Dessa forma, a arquitetura proposta segue os seguintes aspectos:

  
## Arquitetura Proposta:

![Arquitetura do sistema](/docs/images/Diagrama%20Arquitetura.jpg "Arquitetura do sistema")