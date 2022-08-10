import pandas as pd
import redis


def start_controler():
    pass


class WildfireControler:
    def __init__(self,fire_threshold,smoke_threshold) -> None: 
        self.control_df = pd.DataFrame(columns=['device_id','latitude','longitude'])
        self.fire_threshold = fire_threshold
        self.smoke_threshold = smoke_threshold
        pass

    def connect_redis(self,redis_port,redis_hostname):
        self.redis_at = redis.Redis(host=redis_hostname,port=redis_port)
        pass
    
    def insert_point(self,device_id,latitude,longitude):
        if len(self.control_df[self.control_df['device_id'] == device_id]) == 0:
            self.control_df.append([device_id,latitude,longitude])
        self.control_df.append([device_id,latitude,longitude,0,0,0])
        pass

    def check_redis(self,device):
        # Verificar cada device de 30s a 30s        
        pass


    def run(self,check_time):
                
        pass
        
if __name__ == '__main__':
    start_controler()