import requests
import random
import json
import time 


class SensorSimulate:
    def __init__(self,config_dict) -> None:
        self.device_id = config_dict["id"]
        self.temp = config_dict["initial_temperature"]
        self.humidity =  config_dict["initial_humidity"]
        self.latitude = config_dict["latitude"]
        self.longitude = config_dict["longitude"]
        self.delay = config_dict["delay_time"]
        self.run(self.delay)

    def run(self,frequency):
        while True:
            t_sum_or_sub = random.random()
            h_sum_or_sub = random.random()
            t_multiplier = random.randint(1,3)
            h_multiplier = random.randint(1,3)
            temp = random.random()
            humi = random.random()

            if t_sum_or_sub > 0.5:
                self.temp = self.temp + temp*t_multiplier 
            else:
                self.temp = self.temp - temp*t_multiplier 

            if h_sum_or_sub > 0.5:
                self.humidity = self.humidity + humi*h_multiplier 
            else:
                self.humidity = self.humidity - humi*h_multiplier 

            fields = {
                "device_id":self.device_id,
                "temperature":self.temp,
                "humidity":self.humidity,
                "lat":self.latitude,
                "lon":self.longitude
                }   
            json_object = json.dumps(fields, indent = 4) 

            r = requests.post('http://127.0.0.1:8000/insert_data/',data = json_object)
            print("Message Sent:", str(json_object))
            print(r.text)
            time.sleep(frequency)

#%%

# sensor1 = SensorSimulate(device_id=1,init_temp=20,init_humidity=30,latitude= 22.54,longitude=334.53,delay_time=1)


