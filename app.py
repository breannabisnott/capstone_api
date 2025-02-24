from fastapi import FastAPI, Query
import psycopg
from psycopg.rows import dict_row
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [ "http://127.0.0.1:5501" , "http://localhost:5501", "http://fyahalarm.com", "https://fyahalarm.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SensorData(BaseModel):
    id: int = None 
    device_id: str
    time_stamp: datetime = None
    temperature: float
    flame: bool
    flame_level: float
    gas: bool
    gas_concentration: float
    oxygen_concentration: float

def get_db_connection():
    return psycopg.connect(dbname=os.getenv("DB_NAME"), host=os.getenv("DB_HOST"), password=os.getenv("DB_PASS"), user= os.getenv("DB_USER"), row_factory=dict_row)

@app.post("/data")
async def new_data(request:SensorData):
    request.time_stamp = datetime.now()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into sensor_data
                (device_id, time_stamp, temperature, flame, flame_level, gas, gas_concentration, oxygen_concentration) 
                values
                (%s, %s, %s, %s, %s, %s, %s, %s)
                """, 
                (request.device_id, request.time_stamp, request.temperature, request.flame, request.flame_level, request.gas, request.gas_concentration, request.oxygen_concentration)
            )
            conn.commit()
    return {"message": "success"}

@app.get("/data/{device_id}")
async def get_all_data(device_id: str, page_size:int = Query(None, description="number of records returned"), page_number:int = Query(None, description="number of records to offset by")):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """select * from sensor_data where device_id = %s order by time_stamp limit %s offset %s*%s
                """, (device_id, page_size, page_size, page_number)
            )
            sensordata = cur.fetchall()
    return sensordata

@app.get("/latestData/{device_id}")
async def get_latest_data(device_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """select * from sensor_data WHERE device_id = %s order by time_stamp desc LIMIT 1;
                """, [device_id]
            )
            latestdata = cur.fetchall()
    return latestdata