# Módulo de sensoriamento

## Conexão Arduino - Sensor UHT
A ligação entre o sensor de temperatura e o arduino Uno deve ser feita da seguinte forma:

![Esquema Sensor Temperatura](/docs/images/img01_como_usar_com_arduino_sensor_de_umidade_e_temperatura_dht11_uno_mega_2560_nano_leonardo_automacao_residencial.jpg "Esquema Sensor Temperatura")


## Conexão Arduino - Modulo WiFi

### Subindo o Módulo de Controle

- Subir o Redis
- Subir a API

### Acesso 
- Para realizar requisições dentro da mesma máquina, apontaremos pro localhoost (ou seja 127.0.0.1:8000)

- Para realizar requisições dentro da mesma rede (em maquinas diferentes), apontaremos pro ip da maquina do servidor
    - Formas de saber o IP do Servidor: https://linuxhint.com/find-ip-address-ubuntu/

