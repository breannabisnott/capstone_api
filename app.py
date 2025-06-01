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

origins = [ "http://127.0.0.1:5501" , "http://localhost:5501", "http://fyahalarm.com", "https://fyahalarm.com", "http://127.0.0.1:8000"]

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

class SettingsData(BaseModel):
    # id: int = None 
    alert_email: str
    fire_email: str
    hospital_email:str
    temp_thresh: float
    gas_thresh: float

class UpdateAlertEmail(BaseModel):
    alert_email: str

class UpdateFireEmail(BaseModel):
    fire_email: str

class UpdateHospitalEmail(BaseModel):
    hospital_email: str

class UpdateTempThresh(BaseModel):
    temp_thresh: float

class UpdateGasThresh(BaseModel):
    gas_thresh: float

def get_db_connection():
    return psycopg.connect(dbname=os.getenv("DB_NAME"), host=os.getenv("DB_HOST"), password=os.getenv("DB_PASS"), user= os.getenv("DB_USER"), row_factory=dict_row)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "bxscuit.0@gmail.com"
SENDER_PASSWORD = "wauk ihqr hjml nuay"  # Use App Password if using Gmail
RECEIVER_EMAIL = "breanna.bisnott@gmail.com"

def send_email_alert(device_id: str, lat: float, lng:float, alert_email:str, fire_email:str, hospital_email:str):
    """Send an email alert when sensor value is 0."""
    subject = f"🚨 FIRE DETECTED!"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Open Sans', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 0;
                background-color: #E5D0AC;
            }}
            .email-container {{
                background-color: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 20px 0;
            }}
            .header {{
                background-color: #430707;
                color: #ffffff; /* Changed to pure white */
                padding: 25px;
                text-align: center;
                font-family: 'Montserrat', Arial, sans-serif;
            }}
            .logo {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #ffffff; /* Changed to white */
            }}
            .website-link {{
                color: #ffffff !important; /* Forced white */
                text-decoration: none;
                font-size: 14px;
                display: inline-block;
                margin-top: 10px;
            }}
            .content {{
                padding: 25px;
                background-color: white;
                border-left: 4px solid #6d1111;
            }}
            .alert-title {{
                color: #430707;
                border-bottom: 2px solid #bd9999;
                padding-bottom: 10px;
            }}
            .map-link {{
                display: inline-block;
                margin: 15px 0;
                padding: 12px 20px;
                background-color: #6d1111;
                color: #ffffff !important; /* Forced white */
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 16px;
                transition: background-color 0.3s;
            }}
            .map-link:hover {{
                background-color: #430707; /* Darker on hover */
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #777;
                text-align: center;
                padding: 15px;
                border-top: 1px solid #E5D0AC;
                background-color: #faf5f5;
            }}
            .footer a {{
                color: #6d1111;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">Fyah Alarm</div>
                <h2 style="margin: 10px 0; font-size: 28px; letter-spacing: 1px; color: #ffffff;">🔥 FIRE ALERT DETECTED 🔥</h2>
                <h3 style="margin: 5px 0; font-weight: normal; color: #ffffff;">Device: {device_id}</h3>
                <a href="https://fyahalarm.com" class="website-link" style="color: #ffffff;">Visit Our Website</a>
            </div>
            
            <div class="content">
                <h4 class="alert-title">Alert Details</h4>
                <p><strong style="color: #430707;">Warning!</strong> A flame has been detected by device <strong>{device_id}</strong>.</p>
            
                <h4 style="margin-bottom: 10px; color: #6d1111;">📍 Location Details:</h4>
                <ul style="margin-top: 5px;">
                    <li>Latitude: {lat}</li>
                    <li>Longitude: {lng}</li>
                </ul>
                
                <a href="https://www.google.com/maps?q={lat},{lng}" 
                   class="map-link" 
                   target="_blank"
                   style="color: #ffffff;"> 
                   View on Google Maps
                </a>
                
                <p style="margin-top: 20px;">Please take immediate action and verify the situation.</p>
                
                <div style="margin-top: 25px; padding: 15px; background-color: #faf5f5; border-radius: 4px;">
                    <p style="margin: 0; color: #430707;">For more information, visit our dashboard:</p>
                    <a href="https://fyahalarm.com/overview.html" 
                       style="color: #6d1111; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 8px;">
                       https://fyahalarm.com/overview.html
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated alert from your fire detection system.</p>
                <p>© {datetime.now().year} Fyah Alarm | <a href="https://fyahalarm.com">fyahalarm.com</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    # Prepare email
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    recipients = [alert_email, fire_email, hospital_email]
    msg["To"] = ", ".join(recipients)  # Fix: use comma-separated string
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    # plain_text = (
    #     f"Warning! Device {device_id} has detected a flame.\n\n"
    #     f"Location:\nLatitude: {lat}\nLongitude: {lng}\n\n"
    #     f"Google Maps link: https://www.google.com/maps?q={lat},{lng}\n\n"
    #     "Please check the system immediately."
    # )
    # msg.attach(MIMEText(plain_text, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipients, msg.as_string())  # Send to all at once
        print(f"✅ Email alert sent for Device {device_id}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def send_o2_email_alert(device_id: str, lat: float, lng:float, alert_email:str, fire_email:str, hospital_email:str):
    """Send an email alert when sensor value is 0."""
    subject = f"🚨 Fire & Dangerous O2 Levels detected!"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Open Sans', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 0;
                background-color: #E5D0AC;
            }}
            .email-container {{
                background-color: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 20px 0;
            }}
            .header {{
                background-color: #430707;
                color: #ffffff; /* Changed to pure white */
                padding: 25px;
                text-align: center;
                font-family: 'Montserrat', Arial, sans-serif;
            }}
            .logo {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #ffffff; /* Changed to white */
            }}
            .website-link {{
                color: #ffffff !important; /* Forced white */
                text-decoration: none;
                font-size: 14px;
                display: inline-block;
                margin-top: 10px;
            }}
            .content {{
                padding: 25px;
                background-color: white;
                border-left: 4px solid #6d1111;
            }}
            .alert-title {{
                color: #430707;
                border-bottom: 2px solid #bd9999;
                padding-bottom: 10px;
            }}
            .map-link {{
                display: inline-block;
                margin: 15px 0;
                padding: 12px 20px;
                background-color: #6d1111;
                color: #ffffff !important; /* Forced white */
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 16px;
                transition: background-color 0.3s;
            }}
            .map-link:hover {{
                background-color: #430707; /* Darker on hover */
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #777;
                text-align: center;
                padding: 15px;
                border-top: 1px solid #E5D0AC;
                background-color: #faf5f5;
            }}
            .footer a {{
                color: #6d1111;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">Fyah Alarm</div>
                <h2 style="margin: 10px 0; font-size: 28px; letter-spacing: 1px; color: #ffffff;">🔥 FIRE ALERT DETECTED 🔥</h2>
                <h3 style="margin: 5px 0; font-weight: normal; color: #ffffff;">Device: {device_id}</h3>
                <a href="https://fyahalarm.com" class="website-link" style="color: #ffffff;">Visit Our Website</a>
            </div>
            
            <div class="content">
                <h4 class="alert-title">Alert Details</h4>
                <p><strong style="color: #430707;">Warning!</strong> A flame and dangerous oxygen levels have been detected by device <strong>{device_id}</strong>.</p>
            
                <h4 style="margin-bottom: 10px; color: #6d1111;">📍 Location Details:</h4>
                <ul style="margin-top: 5px;">
                    <li>Latitude: {lat}</li>
                    <li>Longitude: {lng}</li>
                </ul>
                
                <a href="https://www.google.com/maps?q={lat},{lng}" 
                   class="map-link" 
                   target="_blank"
                   style="color: #ffffff;"> 
                   View on Google Maps
                </a>
                
                <p style="margin-top: 20px;">Please send an ambulance and take immediate action and verify the situation.</p>
                
                <div style="margin-top: 25px; padding: 15px; background-color: #faf5f5; border-radius: 4px;">
                    <p style="margin: 0; color: #430707;">For more information, visit our dashboard:</p>
                    <a href="https://fyahalarm.com/overview.html" 
                       style="color: #6d1111; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 8px;">
                       https://fyahalarm.com/overview.html
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated alert from your fire detection system.</p>
                <p>© {datetime.now().year} Fyah Alarm | <a href="https://fyahalarm.com">fyahalarm.com</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    # Prepare email
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    recipients = [alert_email, fire_email, hospital_email]
    msg["To"] = ", ".join(recipients)  # Fix: use comma-separated string
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipients, msg.as_string())  # Send to all at once
        print(f"✅ Email alert sent for Device {device_id}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def send_temp_threshold_email(device_id: str, lat: float, lng:float, alert_email:str):
    """Send an email alert when sensor value is 0."""
    subject = f"🚨 HIGH TEMPERATURE DETECTED!"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Open Sans', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 0;
                background-color: #E5D0AC;
            }}
            .email-container {{
                background-color: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 20px 0;
            }}
            .header {{
                background-color: #430707;
                color: #ffffff; /* Changed to pure white */
                padding: 25px;
                text-align: center;
                font-family: 'Montserrat', Arial, sans-serif;
            }}
            .logo {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #ffffff; /* Changed to white */
            }}
            .website-link {{
                color: #ffffff !important; /* Forced white */
                text-decoration: none;
                font-size: 14px;
                display: inline-block;
                margin-top: 10px;
            }}
            .content {{
                padding: 25px;
                background-color: white;
                border-left: 4px solid #6d1111;
            }}
            .alert-title {{
                color: #430707;
                border-bottom: 2px solid #bd9999;
                padding-bottom: 10px;
            }}
            .map-link {{
                display: inline-block;
                margin: 15px 0;
                padding: 12px 20px;
                background-color: #6d1111;
                color: #ffffff !important; /* Forced white */
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 16px;
                transition: background-color 0.3s;
            }}
            .map-link:hover {{
                background-color: #430707; /* Darker on hover */
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #777;
                text-align: center;
                padding: 15px;
                border-top: 1px solid #E5D0AC;
                background-color: #faf5f5;
            }}
            .footer a {{
                color: #6d1111;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">Fyah Alarm</div>
                <h2 style="margin: 10px 0; font-size: 28px; letter-spacing: 1px; color: #ffffff;">🔥 HIGH TEMPERATURE DETECTED 🔥</h2>
                <h3 style="margin: 5px 0; font-weight: normal; color: #ffffff;">Device: {device_id}</h3>
                <a href="https://fyahalarm.com" class="website-link" style="color: #ffffff;">Visit Our Website</a>
            </div>
            
            <div class="content">
                <h4 class="alert-title">Alert Details</h4>
                <p><strong style="color: #430707;">Warning!</strong> Device <strong>{device_id}</strong> has detected a tempeature above your designated threshold.</p>
            
                <h4 style="margin-bottom: 10px; color: #6d1111;">📍 Location Details:</h4>
                <ul style="margin-top: 5px;">
                    <li>Latitude: {lat}</li>
                    <li>Longitude: {lng}</li>
                </ul>
                
                <a href="https://www.google.com/maps?q={lat},{lng}" 
                   class="map-link" 
                   target="_blank"
                   style="color: #ffffff;"> 
                   View on Google Maps
                </a>
                
                <p style="margin-top: 20px;">Please take immediate action and verify the situation.</p>
                
                <div style="margin-top: 25px; padding: 15px; background-color: #faf5f5; border-radius: 4px;">
                    <p style="margin: 0; color: #430707;">For more information, visit our dashboard:</p>
                    <a href="https://fyahalarm.com/overview.html" 
                       style="color: #6d1111; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 8px;">
                       https://fyahalarm.com/overview.html
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated alert from your fire detection system.</p>
                <p>© {datetime.now().year} Fyah Alarm | <a href="https://fyahalarm.com">fyahalarm.com</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = alert_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, alert_email, msg.as_string())
        print(f" Temp Email alert sent for Device {device_id}")
    except Exception as e:
        print(f" Failed to send email: {e}")

def send_gas_threshold_email(device_id: str, lat: float, lng:float, alert_email:str):
    """Send an email alert when sensor value is 0."""
    subject = f"🚨 HIGH GAS CONCENTRATION DETECTED!"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Open Sans', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 0;
                background-color: #E5D0AC;
            }}
            .email-container {{
                background-color: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 20px 0;
            }}
            .header {{
                background-color: #430707;
                color: #ffffff; /* Changed to pure white */
                padding: 25px;
                text-align: center;
                font-family: 'Montserrat', Arial, sans-serif;
            }}
            .logo {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #ffffff; /* Changed to white */
            }}
            .website-link {{
                color: #ffffff !important; /* Forced white */
                text-decoration: none;
                font-size: 14px;
                display: inline-block;
                margin-top: 10px;
            }}
            .content {{
                padding: 25px;
                background-color: white;
                border-left: 4px solid #6d1111;
            }}
            .alert-title {{
                color: #430707;
                border-bottom: 2px solid #bd9999;
                padding-bottom: 10px;
            }}
            .map-link {{
                display: inline-block;
                margin: 15px 0;
                padding: 12px 20px;
                background-color: #6d1111;
                color: #ffffff !important; /* Forced white */
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 16px;
                transition: background-color 0.3s;
            }}
            .map-link:hover {{
                background-color: #430707; /* Darker on hover */
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #777;
                text-align: center;
                padding: 15px;
                border-top: 1px solid #E5D0AC;
                background-color: #faf5f5;
            }}
            .footer a {{
                color: #6d1111;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">Fyah Alarm</div>
                <h2 style="margin: 10px 0; font-size: 28px; letter-spacing: 1px; color: #ffffff;">🔥 GAS DETECTED 🔥</h2>
                <h3 style="margin: 5px 0; font-weight: normal; color: #ffffff;">Device: {device_id}</h3>
                <a href="https://fyahalarm.com" class="website-link" style="color: #ffffff;">Visit Our Website</a>
            </div>
            
            <div class="content">
                <h4 class="alert-title">Alert Details</h4>
                <p><strong style="color: #430707;">Warning!</strong> Device <strong>{device_id}</strong> has detected a gas level above your designated threshold.</p>
            
                <h4 style="margin-bottom: 10px; color: #6d1111;">📍 Location Details:</h4>
                <ul style="margin-top: 5px;">
                    <li>Latitude: {lat}</li>
                    <li>Longitude: {lng}</li>
                </ul>
                
                <a href="https://www.google.com/maps?q={lat},{lng}" 
                   class="map-link" 
                   target="_blank"
                   style="color: #ffffff;"> 
                   View on Google Maps
                </a>
                
                <p style="margin-top: 20px;">Please take immediate action and verify the situation.</p>
                
                <div style="margin-top: 25px; padding: 15px; background-color: #faf5f5; border-radius: 4px;">
                    <p style="margin: 0; color: #430707;">For more information, visit our dashboard:</p>
                    <a href="https://fyahalarm.com/overview.html" 
                       style="color: #6d1111; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 8px;">
                       https://fyahalarm.com/overview.html
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated alert from your fire detection system.</p>
                <p>© {datetime.now().year} Fyah Alarm | <a href="https://fyahalarm.com">fyahalarm.com</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = alert_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, alert_email, msg.as_string())
        print(f" Temp Email alert sent for Device {device_id}")
    except Exception as e:
        print(f" Failed to send email: {e}")

@app.post("/send-email")
async def send_email(
    pdf: UploadFile = File(...),
    email: str = Form(...)
):
    try:
        # Create the multipart email
        msg = MIMEMultipart("mixed")
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg["Subject"] = "🔥 Fyah Alarm Incident Report"

        # Styled HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Open Sans', Arial, sans-serif;
                    background-color: #E5D0AC;
                    margin: 0; padding: 0;
                }}
                .email-container {{
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin: 20px auto;
                    max-width: 600px;
                }}
                .header {{
                    background-color: #430707;
                    color: white;
                    text-align: center;
                    padding: 25px;
                    font-family: 'Montserrat', Arial, sans-serif;
                }}
                .logo {{ font-size: 24px; font-weight: bold; }}
                .content {{
                    padding: 25px;
                    border-left: 4px solid #6d1111;
                }}
                .footer {{
                    font-size: 12px;
                    color: #777;
                    text-align: center;
                    padding: 15px;
                    background-color: #faf5f5;
                    border-top: 1px solid #E5D0AC;
                }}
                a {{
                    color: #6d1111;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">Fyah Alarm</div>
                    <h2>🔥 INCIDENT REPORT 🔥</h2>
                    <a href="https://fyahalarm.com" style="color: white;">Visit Our Website</a>
                </div>
                <div class="content">
                    <h4 style="color:#430707;">Attached Report</h4>
                    <p>Please find the incident report PDF attached to this email.</p>
                    <p>For more information, you can visit your dashboard:</p>
                    <a href="https://fyahalarm.com/overview.html">https://fyahalarm.com/overview.html</a>
                </div>
                <div class="footer">
                    <p>This is an automated alert from your fire detection system.</p>
                    <p>© {datetime.now().year} Fyah Alarm | <a href="https://fyahalarm.com">fyahalarm.com</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        # Attach HTML body
        html_part = MIMEText(html_body, "html")
        alt_part = MIMEMultipart("alternative")
        alt_part.attach(html_part)
        msg.attach(alt_part)

        # Attach PDF
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(await pdf.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{pdf.filename}"')
        msg.attach(part)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        return JSONResponse(content={"message": "Email sent with styled body and PDF attached."}, status_code=200)

    except smtplib.SMTPException as e:
        return JSONResponse(content={"message": f"SMTP error: {str(e)}"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"message": f"Error: {str(e)}"}, status_code=500)
    
@app.post("/data")
async def new_data(request:SensorData):
    request.time_stamp = datetime.now()
    messages = []

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
            # Fetch the current settings from DB
            cur.execute("""SELECT alert_email, fire_email, hospital_email, temp_thresh, gas_thresh FROM settings_data LIMIT 1""")
            row = cur.fetchone()

            alert_email = row["alert_email"]
            fire_email = row["fire_email"]
            hospital_email = row["hospital_email"]
            temp_thresh = float(row["temp_thresh"])
            gas_thresh = float(row["gas_thresh"])


            for email in [alert_email, fire_email, hospital_email]:
                if not email or "@" not in email:
                    return {"message": f"Invalid email address in settings: {email}"}

            # Check for conditions
            if request.flame_level < 2048 and request.temperature > temp_thresh and request.gas_concentration > gas_thresh:
                if request.oxygen_concentration < 19.5:
                    send_o2_email_alert(request.device_id, request.lat, request.lng, alert_email, fire_email, hospital_email)
                    messages.append("Fire & O2 alert sent!")
                else:
                    send_email_alert(request.device_id, request.lat, request.lng, alert_email, fire_email, hospital_email)
                    messages.append("Fire alert sent!")

            elif request.temperature > temp_thresh:
                send_temp_threshold_email(request.device_id, request.lat, request.lng, alert_email)
                messages.append("Temp threshold alert sent!")
            elif request.gas_concentration > gas_thresh:
                send_gas_threshold_email(request.device_id, request.lat, request.lng, alert_email)
                messages.append("Gas threshold alert sent!")

    return {"message": messages or ["Success - No alerts triggered."]}

@app.get("/siren-triggers/{device_id}")
async def get_siren_triggers(device_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get the latest sensor data
            cur.execute(
                """select * from sensor_data WHERE device_id = %s order by time_stamp desc LIMIT 1;
                """, [device_id]
            )
            sensor_data = cur.fetchone()
            
            if not sensor_data:
                return {
                    "fire_trigger": False,
                    "temp_trigger": False,
                    "gas_trigger": False
                }
            
            # Get threshold settings
            cur.execute(
                """SELECT temp_thresh, gas_thresh 
                   FROM settings_data 
                   LIMIT 1"""
            )
            settings = cur.fetchone()
            
            temp_thresh = float(settings["temp_thresh"]) if settings else 50.0
            gas_thresh = float(settings["gas_thresh"]) if settings else 3000.0
            
            # Calculate triggers
            fire_trigger = sensor_data["flame_level"] < 2048 and sensor_data["temperature"] > temp_thresh and sensor_data["gas_concentration"] > gas_thresh
            temp_trigger = sensor_data["temperature"] > temp_thresh
            gas_trigger = sensor_data["gas_concentration"] > gas_thresh
            
            return {
                "fire_trigger": bool(fire_trigger),
                "temp_trigger": bool(temp_trigger),
                "gas_trigger": bool(gas_trigger)
            }

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

@app.post("/settingsInfo")
async def new_settings(settings:SettingsData):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into settings_data
                (alert_email, fire_email, hospital_email, temp_thresh, gas_thresh) 
                values
                (%s, %s, %s, %s, %s)
                """, 
                (settings.alert_email, settings.fire_email, settings.hospital_email, settings.temp_thresh, settings.gas_thresh)
            )
            conn.commit()
    
    return {"settings": "updated"}

@app.patch("/update-alertEmail")
async def update_alert_email(settings: UpdateAlertEmail):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE settings_data SET alert_email = %s WHERE id=1;
                """, 
                (settings.alert_email,)
            )
            conn.commit()
    
    return {"message": "Alert Email Updated"}

@app.patch("/update-fireEmail")
async def update_fire_email(settings: UpdateFireEmail):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE settings_data SET fire_email = %s WHERE id=1;
                """, 
                (settings.fire_email,)
            )
            conn.commit()
    
    return {"message": "Fire Department Email Updated"}

@app.patch("/update-hospitalEmail")
async def update_hospital_email(settings: UpdateHospitalEmail):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE settings_data SET hospital_email = %s WHERE id=1;
                """, 
                (settings.hospital_email,)
            )
            conn.commit()
    
    return {"message": "Hospital Email Updated"}

@app.patch("/update-tempThresh")
async def update_temp_thresh(settings: UpdateTempThresh):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE settings_data SET temp_thresh = %s WHERE id=1;
                """, 
                (settings.temp_thresh,)
            )
            conn.commit()
    
    return {"message": "Temp Thresh updated"}

@app.patch("/update-gasThresh")
async def update_gas_thresh(settings: UpdateGasThresh):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE settings_data SET gas_thresh = %s WHERE id=1;
                """, 
                (settings.gas_thresh,)
            )
            conn.commit()
    
    return {"message": "Gas Threshold Updated"}