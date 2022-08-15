
import pandas as pd
import redis
from datetime import datetime,timedelta
from time import time

redis_hostname = "127.0.0.1"
redis_port = "6379"
time_encode = "%d/%m/%Y, %H:%M:%S"
redis_stream = "temp_data"

def start_controler():
    controler = WildfireControler(30,30,'temp_data')
    controler.connect_redis(redis_port,redis_hostname)
    return controler

def run(controler):
    while True:
        new_msgs = controler.check_redis()
        for msg in new_msgs:
            response = controler.filter_msg(msg)
            if response == "NEW_DEVICE":
                controler.add_device(msg)
            if response == "CHECK_MSG":
                controler.process__msg()

    pass

class WildfireControler:
    def __init__(self,fire_threshold,humidity_threshold,redis_stream) -> None: 
        self.control_df = pd.DataFrame(columns=['device_id','latitude','longitude','heat_warning_level','humidity_warning_level','last_msg_time'])
        self.fire_threshold = fire_threshold
        self.humidity_threshold = humidity_threshold
        self.redis_stream = redis_stream
        self.last_total_msgs = 0
        pass
            

    def connect_redis(self,redis_port,redis_hostname) -> None:
        self.redis_at = redis.Redis(host=redis_hostname,port=redis_port)
        pass
    
    def filter_msg(self,new_msg):
        new_msg = new_msg[1]
        device_id = new_msg[b'device_id'].decode('utf-8')
        device_row = self.control_df[self.control_df['device_id'] == device_id]
        if len(device_row):
            last_msg_time = datetime.strptime(device_row['last_msg_time'],time_encode)
            new_msg_time = datetime.strptime(new_msg[b'time'],time_encode)
            if new_msg_time - last_msg_time > timedelta(0,300,0):
                return "CHECK_MSG"
            else:
                return "NOTHING_TO_DO"
        else:
            return "NEW_DEVICE"
        pass


    def process_msgs(self,new_msg):
        temperature = new_msg[b'temperature'].decode('utf-8')
        humidity = new_msg[b'humidity'].decode('utf-8')
        device_id = new_msg[b'device_id'].decode('utf-8')
        device_row = self.control_df[self.control_df['device_id'] == device_id]
        if temperature > self.fire_threshold:
            device_row['heat_warning_level'] = int(device_row['heat_warning_level']) + 1
        if humidity >self.humidity_threshold:
            device_row['humidity_warning_level'] = int(device_row['humidity_warning_level']) + 1
        
        fields = {'device_id':device_row['device_id'],
        'latitude':device_row['latitude'],
        'longitude':device_row['longitude'],
        'heat_warning_level':device_row['humidity_warning_level'],
        'humidity_warning_level':device_row['humidity_warning_level'],
        'last_msg_time':new_msg[b'time']}
        self.control_df.append(fields,ignore_index=True)
        self.control_df.drop_duplicates(keep='last')
        pass
    

    def check_redis(self):
        total_msgs = len(self.redis_at.xrange(self.redis_stream))
        count_new_msgs = total_msgs - self.last_total_msgs
        self.last_total_msgs = total_msgs
        if count_new_msgs == 0:
            return []
        new_msgs = self.redis_at.xrange(self.redis_stream,count=count_new_msgs)
        return new_msgs
  

if __name__ == '__main__':
    start_controler()
    run()

    #%%