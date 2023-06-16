import requests
import random
import json
import time 
import numpy as np 
import geopy.distance

CONTEXT_PATH = "config/simulation_context.json"

class SensorSimulate:
    """
        Classe responsavel em realizar a simulação do modulo sensorial 
        utilizado no projeto.
    """

    def __init__(self, config_dict: dict) -> None:
        
        self.device_id = config_dict["id"]
        self.temp = config_dict["initial_temperature"]
        self.humidity =  config_dict["initial_humidity"]
        self.latitude = config_dict["latitude"]
        self.longitude = config_dict["longitude"]
        self.delay = config_dict["delay_time"]
        self.fire_distance = None
        self.run(self.delay)
        
    def run(self,frequency: int) -> None:
        """
        Executa a simulação do sensor:
         
           Args:
                frequency (int): Tempo de espera entre duas requisições
           
        """
        while True:
            self.calculate_fire_distance(CONTEXT_PATH)
            
            humidity = self.calculate_humidity(self.humidity,self.fire_distance)

            temperature = self.calculate_temperature(self.temp,self.fire_distance)

            print(f"\nDevice_id: {self.device_id} - Fire Distance: {round(self.fire_distance,2)} m")

            fields = {
                "device_id":self.device_id,
                "temperature":temperature,
                "humidity":humidity,
                "lat":self.latitude,
                "lon":self.longitude
                }   
            json_object = json.dumps(fields, indent = 4) 

            r = requests.post('http://127.0.0.1:8000/insert_data/',data = json_object)
            if r.status_code == 200:
                print(f"Your message has been sent:\n {str(json_object)}")
            else:
                print(f"Something wrong with message:\n {str(json_object)}")
            time.sleep(frequency)


    def calculate_temperature(self, temperature,dist, k=500):
        if dist < 0:
            temperature = temperature + (np.random.normal(0,1,1))
        else:       
            temperature = temperature + k/dist + (np.random.normal(0,1,1))
        return temperature[0]


    def calculate_humidity(self, humidity, dist, k=1):
            if dist < 0:
                humidity =  humidity + (np.random.normal(0,1,1)/100)
            else:   
                humidity =  humidity/np.exp(1/(k*dist)) + (np.random.normal(0,1,1)/100)
            return humidity[0]


    def calculate_fire_distance(self, path, k=3):
        if self.fire_distance == None:
            file = json.load(open(path))["fire"][0]
            self.fire_distance = geopy.distance.geodesic((self.latitude,self.longitude),(file["latitude"],file["longitude"])).m 
        else:
            self.fire_distance = self.fire_distance - random.random()*k
        pass




#%%

# sensor1 = SensorSimulate(device_id=1,init_temp=20,init_humidity=30,latitude= 22.54,longitude=334.53,delay_time=1)


