import schedule 
import pandas as pd
import time
import redis
import json
from typing import Any,List
from datetime import timedelta,datetime
from google.cloud import bigquery
import os


config_file = open("config/server_context.json")
config = json.load(config_file) 
REDIS = config["REDIS"]
CONTROLER = config["WILDFIRE_CONTROLER"]
GCLOUD_SCHEDULER = config["GCLOUD_SCHEDULER"]
os.environ["GCLOUD_PROJECT"] = GCLOUD_SCHEDULER["PROJECT"]

class GcloudScheduler:

    def __init__(self):
        pass
    

    def insert_rows(self,rows):
        client = bigquery.Client()
        table = client.get_table("{}.{}.{}".format(GCLOUD_SCHEDULER["PROJECT"], GCLOUD_SCHEDULER["DATASET"], GCLOUD_SCHEDULER["TABLE"]))

        errors = client.insert_rows_json(table, rows)  # Make an API request.
        if errors == []:
            print("New rows have been added.")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))
        pass

    def structure_data(self, data_compressed: pd.DataFrame):
        row_list = []
        bq_row = {}
        data_compressed = data_compressed.reset_index()
        for device in data_compressed.iterrows():
            device_id = device[1]["device_id"][0]
            device_key = f"controler:device_{device_id}"
            controller_fields = json.loads(self.redis_at.get(device_key).decode("utf-8")) #type: ignore     
            bq_row= {
                "device_id": device_id,
                "max_temperature": device[1]["temperature"]["max"],
                "min_temperature": device[1]["temperature"]["min"],
                "mean_temperature": device[1]["temperature"]["mean"],
                "std_temperature": device[1]["temperature"]["std"],
                "max_humidity": device[1]["temperature"]["max"],
                "min_humidity": device[1]["temperature"]["min"],
                "mean_humidity": device[1]["temperature"]["mean"],
                "std_humidity": device[1]["temperature"]["std"],
                "scheduler": GCLOUD_SCHEDULER["SCHEDULER_RATE"],
                "latitude":controller_fields["latitude"],
                "longitude":controller_fields["longitude"],
                "last_message_recieved_at":controller_fields["last_msg_time"],
                "qty_messages_recieved":controller_fields["qty_msgs_recieved"]
            }
            row_list.append(bq_row.copy())
        return row_list
        
    def export_data(self, data_compressed: pd.DataFrame):
        data_structured=self.structure_data(data_compressed)
        if len(data_structured) > 1:     
            self.insert_rows(data_structured)
            is_sucessful_exported = True
        else:
            is_sucessful_exported = False
        return is_sucessful_exported

    def get_last_message_id(self):
        try:
            last_message_id = self.redis_at.get("last_read_message_key")
            self.last_message_id = last_message_id.decode("utf-8") # type: ignore
        except:
            self.last_message_id = None
        pass

    def get_old_redis_messages(self):
        '''    
        Checks the Redis database for new messages.
        
                Parameters:
                        last_message_id (string): Last message processed id.
                Returns:
                        old_messages (dict) : New messages list.
        '''
        if self.last_message_id:
            old_messages = self.redis_at.xrevrange(REDIS["GENERAL_STREAM"],max=str(self.last_message_id))
        else:
            old_messages= []
        return old_messages

    def delete_data(self,messages_df):
        for key in messages_df["message_key"]:
            self.redis_at.xdel(REDIS["GENERAL_STREAM"],key)
        pass 

    def convert_messages_to_df(self,old_messages):
        old_messages_df = pd.DataFrame()
        for message in old_messages:
            message_key = message[0].decode("utf-8")
            message_content = message[1]
            message_content = {key.decode("utf8"): value.decode("utf8") for key, value in message_content.items()}
            message_content["message_key"] = message_key
            message_content["temperature"] = float(message_content["temperature"])
            message_content["humidity"] = float(message_content["humidity"])
            df_aux = pd.DataFrame([message_content])
            old_messages_df = pd.concat([old_messages_df, df_aux], ignore_index=True)
        return old_messages_df
    
    def compress_data(self):
        self.get_last_message_id()
        old_messages = self.get_old_redis_messages()
        print(old_messages)
        old_messages_df = self.convert_messages_to_df(old_messages)
        print(old_messages_df.head())
        message_stats_df = old_messages_df.groupby("device_id").agg({"temperature": ["min", "max", "mean","std"],"humidity": ["min", "max", "mean","std"]})
        return message_stats_df,old_messages_df
    
    def execute(self):
        data_compressed,messages_df  = self.compress_data()
        # is_sucessful_exported = self.export_data(data_compressed)
        is_sucessful_exported = True
        if is_sucessful_exported:
            self.delete_data(messages_df)

    def check_redis(self):
        self.redis_at = redis.Redis(host=REDIS["HOSTNAME"],port=REDIS["PORT"])
        return self.redis_at.ping()

if __name__ == '__main__':
    scheduler = GcloudScheduler()
    schedule.every(GCLOUD_SCHEDULER["SCHEDULER_RATE"]).seconds.do(scheduler.execute)

    while True:
        is_redis_running = scheduler.check_redis()
        if is_redis_running:
            schedule.run_pending()
            time.sleep(10)
        else:
            break