import redis
import csv
import time
from datetime import datetime

# Configurações do banco Redis
redis_host = '127.0.0.1'  # Substitua pelo host do seu banco Redis
redis_port = 6379         # Porta padrão do Redis

# Arquivo CSV para registro
csv_filename = 'registro_redis_with_optimizer.csv'

# Função para obter o tamanho em bytes do banco Redis
def get_redis_memory_usage(redis_connection):
    memory_info = redis_connection.info("memory")
    used_memory = memory_info["used_memory"]
    return used_memory

# Função para registrar o tamanho em bytes no arquivo CSV
def write_to_csv(filename, timestamp, bytes_used):
    with open(filename, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([timestamp, bytes_used])

if __name__ == "__main__":
    # Conectando ao banco Redis
    redis_connection = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    # Criação do cabeçalho do CSV, se necessário
    with open(csv_filename, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Timestamp', 'Bytes Used'])

    # Loop para monitorar e registrar a cada 10 segundos
    try:
        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            bytes_used = get_redis_memory_usage(redis_connection)
            write_to_csv(csv_filename, timestamp, bytes_used)
            print(f"Registro feito em {timestamp} - Bytes usados: {bytes_used}")
            time.sleep(10)  # Aguarda 10 segundos
    except KeyboardInterrupt:
        print("Monitoramento interrompido pelo usuário.")