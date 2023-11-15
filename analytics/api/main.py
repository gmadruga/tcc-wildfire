from fastapi import FastAPI
from pydantic import BaseModel
import redis
import uvicorn
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

    sensor_stream = f"device_{str(item.device_id)}"
    general_stream = "temp_data"

    time = datetime.now().strftime(time_encode)
    general_fields = {
        "device_id":item.device_id,
        "temperature":item.temperature,
        "humidity":item.humidity,
        "lat":item.lat,
        "lon":item.lon,
        "time":time
        }
    
    device_fields = {
        "temperature":item.temperature,
        "humidity":item.humidity,
        "time":time
    }

    redis_at = redis.Redis(host=redis_hostname,port=redis_port) # type: ignore
    redis_at.xadd(general_stream, general_fields)
    # redis_at.xadd(sensor_stream, device_fields)
    return "SEND"


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)