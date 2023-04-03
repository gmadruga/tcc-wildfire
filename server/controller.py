
import json
import redis
from datetime import datetime,timedelta

config_file = open("/home/gabrielmadruga/Documents/Github/tcc-wildfire/server/config/server_context.json")
config = json.load(config_file) 
REDIS = config["REDIS"]
CONTROLER = config["CONTROLER"]


def run(controler):
    while True:
        new_msgs = controler.check_redis_new_messages()
        for msg in new_msgs:
            response = controler.is_new_device(msg)
            if response:
                controler.process_msgs(msg)
            else:
                controler.add_device(msg)
        controler.check_devices()


class WildfireControler:
    def __init__(self) -> None: 
        self.last_total_msgs = 0
        self.device_ids = [] 
        pass         

    def connect_redis(self) -> None:
        self.redis_at = redis.Redis(host=REDIS["HOSTNAME"],port=REDIS["PORT"])
        pass
    
    def is_new_device(self,new_msg) -> bool:
        new_msg = new_msg[1]
        device_id = int(new_msg[b"device_id"].decode("utf-8"))
        device_key = f"controler:device_{device_id}"
        sensor_status = self.redis_at.get(device_key)
        if sensor_status:
            return True
        return False
    
    def add_device(self,new_msg):
        new_msg = new_msg[1]
        device_id = int(new_msg[b"device_id"].decode("utf-8"))
        latitude = float(new_msg[b"lat"].decode("utf-8"))
        longitude = float(new_msg[b"lon"].decode("utf-8"))
        last_msg = str(new_msg[b"time"].decode("utf-8"))
        fields = {"device_id":device_id,
            "latitude":latitude,
            "longitude":longitude,
            "temperature_warning_level":0,
            "humidity_warning_level":0,
            "last_msg_time":last_msg,
            "qty_msgs_recieved":0,
            "mean_delay_time":0
        }
        device_key = f"controler:device_{device_id}"
        self.redis_at.set(device_key,json.dumps(fields))       
        self.redis_at.lpush(REDIS["DEVICES_KEY"],device_id)

    def process_msgs(self,new_msg):
        new_msg = new_msg[1]
        device_id = int(new_msg[b"device_id"].decode("utf-8"))
        device_key = f"controler:device_{device_id}"
        sensor_status = self.redis_at.get(device_key)

        sensor_status = self.check_sensor(new_msg,sensor_status)

        self.redis_at.set(device_key,json.dumps(sensor_status))
        
        return "STATUS_UPDATED"

    def check_sensor(self,new_msg,actual_status):
        actual_status = json.loads(actual_status.decode("utf-8"))

        if float(new_msg[b"temperature"].decode("utf-8")) > CONTROLER["TEMPERATURE_THRESHOLD"]:
            actual_status["temperature_warning_level"] += 1
        else:
            actual_status["temperature_warning_level"] = 0 

        if float(new_msg[b"humidity"].decode("utf-8")) > CONTROLER["TEMPERATURE_THRESHOLD"]:
            actual_status["humidity_warning_level"] += 1
        else:
            actual_status["humidity_warning_level"] = 0

        qty_msgs = actual_status["qty_msgs_recieved"] 
        mean_delay_time = actual_status["mean_delay_time"] 

        last_msg_time = datetime.strptime(actual_status["last_msg_time"], CONTROLER["TIME_ENCODE"])
        actual_msg_time = datetime.strptime(new_msg[b"time"].decode("utf-8"), CONTROLER["TIME_ENCODE"])
        delta =  actual_msg_time - last_msg_time
        mean_delay_time = ((qty_msgs * mean_delay_time) + delta.seconds)/(qty_msgs + 1)
        
        actual_status["qty_msgs_recieved"] += 1
        actual_status["last_msg_time"] = new_msg[b"time"].decode("utf-8")
        actual_status["mean_delay_time"] = mean_delay_time
  
        return actual_status

    def check_redis_new_messages(self) -> list:
        total_msgs = len(self.redis_at.xrange(REDIS["GENERAL_STREAM"]))
        if self.redis_at.get(REDIS["COUNT_MESSAGES_KEY"]):
            self.last_total_msgs = int(self.redis_at.get(REDIS["COUNT_MESSAGES_KEY"]).decode("utf-8"))

        qty_new_msgs = total_msgs - self.last_total_msgs # type: ignore
        
        if qty_new_msgs == 0:
            return []
        
        new_msgs = self.redis_at.xrevrange(REDIS["GENERAL_STREAM"], count=qty_new_msgs)
        new_msgs.reverse()
        self.redis_at.set(REDIS["COUNT_MESSAGES_KEY"],total_msgs) # type: ignore
        return new_msgs
  
    def check_devices(self):
        
        first_device = int(self.redis_at.lpop(REDIS["DEVICES_KEY"]).decode("utf-8"))
        new_device = -1
        while first_device != new_device:
            if new_device == -1:
                new_device = first_device
            
            device_key = f"controler:device_{new_device}"
            sensor_status = self.redis_at.get(device_key)
            sensor_status = json.loads(sensor_status.decode("utf-8"))  # type: ignore

            if sensor_status["temperature_warning_level"] > CONTROLER["MAX_TEMPERATURE_THRESHOLD"]:
                warning_message = f"[WARNING] Device {new_device}: Temperature higher than expected."
                warning_message = {"message":warning_message}
                self.redis_at.xadd(REDIS["WARNING_KEY"],warning_message)
            
            if sensor_status["humidity_warning_level"] > CONTROLER["MAX_HUMIDITY_THRESHOLD"]:
                warning_message = f"[WARNING] Device {new_device}: Humidity higher than expected."
                warning_message = {"message":warning_message}
                self.redis_at.xadd(REDIS["WARNING_KEY"],warning_message)

            if datetime.strptime(sensor_status["last_msg_time"], CONTROLER["TIME_ENCODE"]) + (timedelta(seconds=sensor_status["mean_delay_time"])*CONTROLER["MAX_FACTOR_WITHOUT_MESSAGE"]) < datetime.now():
                warning_message = f"[WARNING] Device {new_device}: New messages were expected, but they did not appear."
                warning_message = {"message":warning_message}
                self.redis_at.xadd(REDIS["WARNING_KEY"],warning_message)


            self.redis_at.rpush(REDIS["DEVICES_KEY"],new_device)
            new_device = int(self.redis_at.lpop(REDIS["DEVICES_KEY"]).decode("utf-8"))
        self.redis_at.rpush(REDIS["DEVICES_KEY"],new_device)

        pass


if __name__ == '__main__':


    controler = WildfireControler()
    controler.connect_redis()
    run(controler)

    #%%