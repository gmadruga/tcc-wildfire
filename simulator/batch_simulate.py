import json
import _thread
from sensor import SensorSimulate
import multiprocessing 
import concurrent.futures


def simulate(json_path: str):
    """
    Função realiza a leitura de um arquivo .json com uma lista de
    configurações de simulação e as executa em paralelo.
    
    """
    with concurrent.futures.ProcessPoolExecutor() as executor:
        file = open(json_path)
        data = json.load(file) 
        cods = executor.map(SensorSimulate,data["sensors"])            
        for cod in cods:
            print(cod)

if __name__ == '__main__':
    simulate("config/simulation_context.json")