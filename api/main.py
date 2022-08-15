from fastapi import FastAPI
from pydantic import BaseModel
import redis
from datetime import datetime

class Item(BaseModel):
    device_id: int
    temperature: float
    humidity: float
    lat:float
    lon:float



redis_hostname = "127.0.0.1"
redis_port = "6379"
time_encode = "%d/%m/%Y, %H:%M:%S"
app = FastAPI()


@app.post("/insert_data/")
async def insert_data(item: Item):
    stream = "temp_data"
    time = datetime.now().strftime(time_encode)

    fields = {
        "device_id":item.device_id,
        "temperature":item.temperature,
        "humidity":item.humidity,
        "lat":item.lat,
        "lon":item.lon,
        "time":time
        }   
    redis_at = redis.Redis(host=redis_hostname,port=redis_port)
    redis_at.xadd(stream, fields)
    return "SEND"

