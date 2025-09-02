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


def send_email(to_address):
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = SUBJECT
    html = ""
    with open("mail.html", "r") as file:
        html = file.read()

    html_part = MIMEText(html, 'html')
    msg.attach(html_part)
    print("Begining sending process...")
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            status_code, response = server.ehlo()
            print(f"[*] Echoing the server: {status_code} {response}")
            status_code, response= server.starttls()
            print(f"[*] Starting TLS connection: {status_code} {response}")
            status_code, response = server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            print(f"[*] Logging in: {status_code} {response}")
            server.sendmail(EMAIL_ADDRESS, to_address, msg.as_string())
            server.quit()
            print(f"[+] Email sent to {to_address}")
    except Exception as e:
        print(f"[!] Failed to send to {to_address}: {e}")

# --- MAIN LOOP WITH RANDOM DELAYS ---
for recipient in recipients:
    send_email(recipient)
    delay = random.randint(30, 40)
    print(f"Waiting {delay} seconds before next email...")
    time.sleep(delay)

print("Done")