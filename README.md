# Proposta de Arquitetura Para Controle de Incendios Florestais

## Descrição

Esse projeto faz parte da minha tese de conclusão do curso de Engenharia Eletrônica e de Computação pela Universidade Federal do Rio de Janeiro (UFRJ), ele abriga a implementação de um sistema de detecção de incêndios florestais a partir da arquitetura proposta em minha tese. Junto a isso, este repositório também contém os testes e simulações utilizados na avaliação da solução.

## Organização 

Esse repoistório possui o seguinte esquema de diretorios:

```
tcc-wildfire
|
├── analytics
│   ├── api
│   ├── config
│   ├── controller
│   └── scheduler
├── results
├── sensor
└── simulator
    ├── config
    ├── notebooks

```


### Analytics
Código de funcionamento da camada analítica, dividido em 3 processos distintos.

- **API**: Código responsavel pelo levantemento do API destinada a conexão com a camada sensorial.
- **Config**: Arquivo com configurações gerais de gerenciamento dos dispositivos da camada.
- **Controller**: Código responsavel pelo processamento e análise das informações coletadas.
- **Scheduler**: Código responsavel pela limpeza do banco local e envio das informações já processadas para a camada de armazenamento.

### Sensor
Código de funcionamento dos dispositivos localizados na camada sensorial da arquitetura.


### Simulator
Scripts utlizados para a simulação de incêndio realizada no projeto.

- **Config**: Diretório com as configurações gerais das simulações realizadas no projeto.
- **Notebook**: Diretório com os scripts utilizados para criação do ambiente simulado

### Results
Resultados do sistema a partir dos dados simulados.

<!-- ## Modo de Uso -->

