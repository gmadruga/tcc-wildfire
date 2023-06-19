import schedule 
import time
import redis
import json
from datetime import timedelta,datetime


config_file = open("config/server_context.json")
config = json.load(config_file) 
REDIS = config["REDIS"]
CONTROLER = config["WILDFIRE_CONTROLER"]

class GcloudScheduler:

    def __init__(self):
        pass

    def gcloud_routine(self):
        pass

    def compress_data_routine(self):
        pass

    def execute(self):
        self.compress_data_routine()
        self.gcloud_routine()

    def check_redis(self):
        r = redis.Redis(host=REDIS["HOSTNAME"],port=REDIS["PORT"])
        return r.ping()

if __name__ == '__main__':
    scheduler = GcloudScheduler()
    schedule.every(5).minutes.do(scheduler.execute)

    while True:
        is_redis_running = scheduler.check_redis()
        if is_redis_running:
            schedule.run_pending()
            time.sleep(10)
        else:
            break