import json
import redis
from datetime import datetime,timedelta
from typing import Any,List

config_file = open("analytics_layer/config/server_context.json")
config = json.load(config_file) 
REDIS = config["REDIS"]
CONTROLER = config["WILDFIRE_CONTROLER"]

class WildfireControler:

    def __init__(self) -> None: 
        '''
        Class Init Method. Initialize list with devices_id used

                Parameters:
                        None
                Returns:
                        None
                        
        '''
        self.device_ids = [] 
        pass         

    def connect_redis(self) -> None:
        '''    
        Create connection to Redis database

                Parameters:
                        None
                Returns:
                        None
        '''
        self.redis_at = redis.Redis(host=REDIS["HOSTNAME"],port=REDIS["PORT"])
        pass
    
    def is_new_device(self,message: dict) -> bool:
        '''    
        Checks whether the incoming message originates from a new device.

                Parameters:
                        message (dict): Message with device status.
                Returns:
                        is_new_device (bool): Boolean operator informing if the message comes from a device not yet registered.
        '''
        device_id = int(message[b"device_id"].decode("utf-8"))
        device_key = f"controler:device_{device_id}"
        device_status = self.redis_at.get(device_key)
        if device_status:
            is_new_device = False
        else:
            is_new_device= True
        return is_new_device    

    def add_device(self,message: Any) -> None:
        '''    
        Register new device on Redis and process his message.
        
                Parameters:
                        new_msg (dict): Device's first status message.
                Returns:
                        None.
        '''
        device_id = int(message[b"device_id"].decode("utf-8"))
        latitude = float(message[b"lat"].decode("utf-8"))
        longitude = float(message[b"lon"].decode("utf-8"))
        last_msg = str(message[b"time"].decode("utf-8"))
        fields ={
            "device_id":device_id,
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

    def process_message(self,message: Any):
        '''    
        Process message.
        
                Parameters:
                        message (dict): Device's status message.
                Returns:
                        None.
        '''
        device_id = int(message[b"device_id"].decode("utf-8"))
        device_key = f"controler:device_{device_id}"
        actual_device_status = self.redis_at.get(device_key)
        updated_device_status = self.check_device(message,actual_device_status)
        self.redis_at.set(device_key,json.dumps(updated_device_status))
        

    def check_device(self,message: dict, actual_status: Any):
        '''    
        Updates message status.
        
                Parameters:
                        message (dict): Device's status message.
                        actual_status (dict) : Device's actual status information.
                Returns:
                        updated_status (dict) : Device's updated status information.
        '''
        actual_status = json.loads(actual_status.decode("utf-8"))  # type: ignore

        if float(message[b"temperature"].decode("utf-8")) > CONTROLER["TEMPERATURE_THRESHOLD"]:
            actual_status["temperature_warning_level"] += 1
        else:
            actual_status["temperature_warning_level"] = 0 

        if float(message[b"humidity"].decode("utf-8")) > CONTROLER["TEMPERATURE_THRESHOLD"]:
            actual_status["humidity_warning_level"] += 1
        else:
            actual_status["humidity_warning_level"] = 0

        qty_msgs = actual_status["qty_msgs_recieved"] 
        mean_delay_time = actual_status["mean_delay_time"] 

        last_msg_time = datetime.strptime(actual_status["last_msg_time"], CONTROLER["TIME_ENCODE"])
        actual_msg_time = datetime.strptime(message[b"time"].decode("utf-8"), CONTROLER["TIME_ENCODE"])
        delta =  actual_msg_time - last_msg_time
        mean_delay_time = ((qty_msgs * mean_delay_time) + delta.seconds)/(qty_msgs + 1)
        
        actual_status["qty_msgs_recieved"] += 1
        actual_status["last_msg_time"] = message[b"time"].decode("utf-8")
        actual_status["mean_delay_time"] = mean_delay_time
        updated_status = actual_status

        return updated_status

    def check_redis_new_messages(self,last_message_id: str|None) -> list:
        '''    
        Checks the Redis database for new messages.
        
                Parameters:
                        last_message_id (string): Last message processed id.
                Returns:
                        new_messages (dict) : New messages list.
        '''
        self.process_loop_started_at = datetime.now()
        if last_message_id:
            new_messages = self.redis_at.xrevrange(REDIS["GENERAL_STREAM"],min=str(last_message_id))
        else:
            new_messages = self.redis_at.xrevrange(REDIS["GENERAL_STREAM"])
        self.push_last_message_id(new_messages[0])
    
        return new_messages[:-1]
  
    def push_last_message_id(self,message):
        '''    
        Pushes the last message processed id to Redis db.
        
                Parameters:
                        message (string): Last message that will be pushed.
                Returns:
                       None.
        '''
        message_key = message[0].decode('utf-8')
        self.redis_at.set("last_read_message_key",message_key)    

    def get_last_message_id(self) -> str | None:
        '''    
        Pushes the last message processed id to Redis db.
        
                Parameters:
                        message (string): Last message that will be pushed.
                Returns:
                       None.
        '''
        try:
            last_message_id = self.redis_at.get("last_read_message_key")
            last_message_id = last_message_id.decode("utf-8") # type: ignore
        except:
            last_message_id = None
        return last_message_id

    def check_devices(self):
        '''    
        Verifies that devices are performing correctly from collected data.
                Parameters:
                        None.
                Returns:
                       None.
        '''
        first_device = int(self.redis_at.lpop(REDIS["DEVICES_KEY"]).decode("utf-8"))
        new_device = -1
        while first_device != new_device:
            if new_device == -1:
                new_device = first_device
            
            device_key = f"controler:device_{new_device}"
            device_status = self.redis_at.get(device_key)
            device_status = json.loads(device_status.decode("utf-8"))  # type: ignore

            if device_status["temperature_warning_level"] > CONTROLER["MAX_TEMPERATURE_THRESHOLD"]:
                warning_message = f"[WARNING] Device {new_device}: Temperature higher than expected."
                warning_message = {"message":warning_message}
                self.redis_at.xadd(REDIS["WARNING_KEY"],warning_message)
            
            if device_status["humidity_warning_level"] > CONTROLER["MAX_HUMIDITY_THRESHOLD"]:
                warning_message = f"[WARNING] Device {new_device}: Humidity higher than expected."
                warning_message = {"message":warning_message}
                self.redis_at.xadd(REDIS["WARNING_KEY"],warning_message)

            if datetime.strptime(device_status["last_msg_time"], CONTROLER["TIME_ENCODE"]) + (timedelta(seconds=device_status["mean_delay_time"])*CONTROLER["MAX_FACTOR_WITHOUT_MESSAGE"]) < self.process_loop_started_at:
                warning_message = f"[WARNING] Device {new_device}: New messages were expected, but they did not appear."
                warning_message = {"message":warning_message}
                self.redis_at.xadd(REDIS["WARNING_KEY"],warning_message)

            self.redis_at.rpush(REDIS["DEVICES_KEY"],new_device)
            new_device = int(self.redis_at.lpop(REDIS["DEVICES_KEY"]).decode("utf-8"))
        self.redis_at.rpush(REDIS["DEVICES_KEY"],new_device)

        
def run(controler:WildfireControler):
    while True:
        last_message_id = controler.get_last_message_id()
        new_messages = controler.check_redis_new_messages(last_message_id)
        for messsage in new_messages:
            message_content = messsage[1]
            is_new_device = controler.is_new_device(message_content)
            if is_new_device:
                controler.add_device(message_content)
            controler.process_message(message_content)
        controler.check_devices()

if __name__ == '__main__':
    controler = WildfireControler()
    controler.connect_redis()
    run(controler)

    #%%