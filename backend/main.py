import smtplib
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.utils
import os
from dotenv import load_dotenv
from email import charset
import html2text
charset.add_charset("utf-8", charset.QP, charset.QP, "utf-8")

load_dotenv()

# --- CONFIG ---
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")

recipients = [
    "petrusheya@gmail.com",
]

SUBJECT = "Bring along a warm jersey?"
SENDER_NAME = "Petrus Sheya"  # customize this


def send_email(to_address):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{SENDER_NAME} <{EMAIL_ADDRESS}>"
    msg["To"] = to_address
    msg["Subject"] = SUBJECT
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain=EMAIL_ADDRESS.split("@")[1])
    msg["Reply-To"] = EMAIL_ADDRESS
    with open("mail.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # Convert HTML to plain text
    text_content = html2text.html2text(html_content)


    # Attach converted text
    msg.attach(MIMEText(text_content, "plain", "utf-8"))

    # Attach HTML
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    print(f"[*] Preparing to send to {to_address} (Hostinger Webmail fingerprint)")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            status_code, response = server.ehlo()
            print(f"[*] EHLO: {status_code} {response.decode()}")
            status_code, response = server.starttls()
            print(f"[*] STARTTLS: {status_code} {response.decode()}")
            status_code, response = server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            print(f"[*] LOGIN: {status_code} {response.decode()}")
            server.sendmail(EMAIL_ADDRESS, [to_address], msg.as_string())
            print(f"[+] Email sent to {to_address}")
    except Exception as e:
        print(f"[!] Failed to send to {to_address}: {e}")


# --- Main loop ---
for recipient in recipients:
    send_email(recipient)
    delay = random.randint(30, 120)  # random delay between 30s–2min
    print(f"Waiting {delay} seconds before next email...")
    time.sleep(delay)

print("Done")
