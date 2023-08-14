import json
from sensor import SensorSimulate
import concurrent.futures
import sys
import logging

def simulate(json_path: str):
    """
    Função realiza a leitura de um arquivo .json com uma lista de
    configurações de simulação e as executa em paralelo.
    
    """
    with concurrent.futures.ProcessPoolExecutor() as executor:
        logging.basicConfig(filename=f'{json_path}.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        file = open(json_path)
        data = json.load(file) 
        cods = executor.map(SensorSimulate,data["sensors"])
        try:            
            for cod in cods:
                print(cod)
        except:
            print("Todos os sensores pararam de responder")

if __name__ == '__main__':    
    if len(sys.argv) != 2:
        print("Uso: python3 batch_simulate.py <filepath> ")
        sys.exit(1)
    simulate(sys.argv[1])
