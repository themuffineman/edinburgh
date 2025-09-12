import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.utils
import os
from dotenv import load_dotenv
from email import charset
import html2text
from pydantic import BaseModel
from typing import List

charset.add_charset("utf-8", charset.QP, charset.QP, "utf-8")

load_dotenv()

# --- CONFIG ---
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 587
# EMAIL_ADDRESS_1 = os.getenv("SENDER_EMAIL_1")
# EMAIL_ADDRESS_2 = os.getenv("SENDER_EMAIL_2")
# EMAIL_ADDRESS_3 = os.getenv("SENDER_EMAIL_3")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")
SENDER_NAME = "Petrus Sheya"  # customize this

class EmailRequest(BaseModel):
    recipients: List[str]
    subject: str
    body_text: str
    sender_name: str = SENDER_NAME

def convert_text_to_html(body_text: str) -> str:
    """
    Convert plain text body to HTML format by creating <p> tags for each line break.
    """
    # Split text by line breaks and filter out empty lines
    lines = [line.strip() for line in body_text.split('\n') if line.strip()]
    
    # Convert each line to a paragraph
    html_paragraphs = [f"<p>{line}</p>" for line in lines]
    
    # Create full HTML structure
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            p {{
                margin-bottom: 16px;
            }}
        </style>
    </head>
    <body>
        {''.join(html_paragraphs)}
    </body>
    </html>
    """
    
    return html_body

def send_email(to_address: str, subject: str, body_text: str, sender_name: str, email_inbox:str):
    EMAIL_ADDRESS = email_inbox
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{sender_name} <{EMAIL_ADDRESS}>"
    msg["To"] = to_address
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain=EMAIL_ADDRESS.split("@")[1])
    msg["Reply-To"] = EMAIL_ADDRESS

    # Convert plain text body to HTML format
    html_content = convert_text_to_html(body_text)
    
    # Use the original body_text as plain text version
    text_content = body_text

    # Attach plain text version
    msg.attach(MIMEText(text_content, "plain", "utf-8"))

    # Attach HTML version
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
            return True, None
    except Exception as e:
        print(f"[!] Failed to send to {to_address}: {e}")
        return False, str(e)
