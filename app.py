from fastapi import FastAPI, Query, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import smtplib
from email.mime.base import MIMEBase
from email import encoders
import psycopg
from psycopg.rows import dict_row
from pydantic import BaseModel, EmailStr
from datetime import datetime
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

class EmailSchema(BaseModel):
    email: List[EmailStr]

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
    humidity: float
    lat: float
    lng: float
    accuracy: float

def get_db_connection():
    return psycopg.connect(dbname=os.getenv("DB_NAME"), host=os.getenv("DB_HOST"), password=os.getenv("DB_PASS"), user= os.getenv("DB_USER"), row_factory=dict_row)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "bxscuit.0@gmail.com"
SENDER_PASSWORD = "wauk ihqr hjml nuay"  # Use App Password if using Gmail
RECEIVER_EMAIL = "breanna.bisnott@gmail.com"

def send_email_alert(device_id: str):
    """Send an email alert when sensor value is 0."""
    subject = f"🚨 FIRE DETECTED by device: {device_id}!"
    body = f"Warning! Device {device_id} has detected a flame. Please check the system immediately."
    
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print(f" Email alert sent for Device {device_id}")
    except Exception as e:
        print(f" Failed to send email: {e}")

@app.post("/send-email")
async def send_email(pdf: UploadFile = File(...), email: str = Form(...)):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = 'Incident Report PDF'

        # Attach the PDF
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(await pdf.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{pdf.filename}"')
        msg.attach(part)

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        return JSONResponse(content={"message": "Email sent successfully!"}, status_code=200)

    except smtplib.SMTPException as e:
        return JSONResponse(content={"message": f"Failed to send email: {str(e)}"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"message": f"An unexpected error occurred: {str(e)}"}, status_code=500)
    
@app.post("/data")
async def new_data(request:SensorData):
    request.time_stamp = datetime.now()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into sensor_data
                (device_id, time_stamp, temperature, flame, flame_level, gas, gas_concentration, oxygen_concentration, humidity, lat, lng, accuracy) 
                values
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, 
                (request.device_id, request.time_stamp, request.temperature, request.flame, request.flame_level, request.gas, request.gas_concentration, request.oxygen_concentration, request.humidity, request.lat, request.lng, request.accuracy)
            )
            conn.commit()
    if request.flame == 1:
        send_email_alert(request.device_id)
        return {"message": "Alert sent!", "sensor_id": request.device_id}
    
    return {"message": "success"}

@app.get("/data/{device_id}")
async def get_all_data(device_id: str, page_size:int = Query(None, description="number of records returned"), page_number:int = Query(None, description="number of records to offset by")):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """select * from sensor_data where device_id = %s order by time_stamp desc limit %s offset %s*%s
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

@app.get("/latestLocation/{device_id}")
async def get_latest_data(device_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """select lat, lng from sensor_data WHERE device_id = %s order by time_stamp desc LIMIT 1;
                """, [device_id]
            )
            latestdata = cur.fetchall()
    return latestdata

#test