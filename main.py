import smtplib
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
load_dotenv()


# --- CONFIG ---
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 465 
EMAIL_ADDRESS = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

recipients = [
    "petrusheya@gmail.com",
]

SUBJECT = "Hello Old Friend. Ready for the tech-con?"
BODY = """
Hi there Petrus,

Just checking in if everything is ok? 
If you need me to acompany you to the tech coference, just say the word

"""

def send_email(to_address):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = SUBJECT

    msg.attach(MIMEText(BODY, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"[+] Email sent to {to_address}")
    except Exception as e:
        print(f"[!] Failed to send to {to_address}: {e}")

# --- MAIN LOOP WITH RANDOM DELAYS ---
for recipient in recipients:
    send_email(recipient)
    delay = random.randint(30, 40)
    print(f"Waiting {delay} seconds before next email...")
    time.sleep(delay)

print("All emails sent!")