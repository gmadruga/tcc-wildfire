import requests
import random
import json
import time 
import math
import numpy as np 
import pandas as pd

CONTEXT_PATH = "simulator/config/qty_sensor_01/data/sensor_data_1.csv"

class SensorSimulate:
    """
        Classe responsavel em realizar a simulação do modulo sensorial 
        utilizado no projeto.
    """

    def __init__(self, config_dict: dict) -> None:
        
        self.device_id = config_dict["id"]
        self.latitude = config_dict["latitude"]
        self.longitude = config_dict["longitude"]
        self.delay = config_dict["delay_time"]
        self.burned = False
        self.step = 0
        self.run(self.delay)
        
    def run(self,delay_time: int) -> None:
        """
        Executa a simulação do sensor:
         
           Args:
                delay_time (int): Tempo de espera entre duas requisições
           
        """

        df = pd.read_csv(CONTEXT_PATH)
        df = df[df["id"]==self.device_id]

        while self.burned == False:
            self.step = self.step +1
            actual_row = df[df["step"]==self.step]

            actual_temperature = actual_row.temperature.values[0]
            actual_humidity = actual_row.humidity.values[0]
            
            if actual_temperature > 55:
                self.burned = True
                break

            if self.step%self.delay == 0:
                
                fields = {
                    "device_id":self.device_id,
                    "temperature":actual_humidity,
                    "humidity":actual_temperature,
                    "lat":self.latitude,
                    "lon":self.longitude
                    }   
                json_object = json.dumps(fields, indent = 4) 
                print(json_object)
                r = requests.post('http://127.0.0.1:8000/insert_data/',data = json_object)
                if r.status_code == 200:
                    print(f"Your message has been sent:\n {str(json_object)}")
                else:
                    print(f"Something wrong with message:\n {str(json_object)}")

            time.sleep(1)



#%%


context = {
        "id": 3,
        "initial_temperature": 25,
        "initial_humidity": 70,
        "latitude": -22.939777,
        "longitude": -43.29419823,
        "pixel_position_x":75,
        "pixel_position_y":75,
        "delay_time": 10
}

# sensor1 = SensorSimulate(context)


