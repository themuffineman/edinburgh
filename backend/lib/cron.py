import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
from lib import send_email_func
import time
import random
load_dotenv()

# Load your Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_scheduled_emails(supabase: Client):
    # Current time (UTC, to the minute)
    current_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)

    # Define a 10-minute window around current time
    window_start = current_time - timedelta(minutes=15)
    window_end = current_time + timedelta(minutes=15)

    # Query rows within the time window
    response = (
        supabase.table("scheduled-emails")
        .select("*")
        .gte("scheduled_time", window_start.isoformat())
        .lte("scheduled_time", window_end.isoformat())
        .eq("sent", False) 
        .execute()
    )

    return response.data or []

def send_email(record):
    try:
        payload = {
            "recipient": record.get("recipient"),
            "subject": record.get("subject", "No Subject"),
            "body": record.get("body_text", "No Content"),
            "sender_name": record.get("sender_name", "No Content"),
            "id": record.get("id"),
            "email_inbox": record.get("mailbox")
        }
        success, error_message = send_email_func.send_email(
            to_address=payload["recipient"],
            subject=payload["subject"],
            body_text=payload["body"],
            sender_name=payload["sender_name"],
            email_inbox=payload["email_inbox"]
        )
        if success:
            mark_as_sent(supabase_client, payload["id"])
            print(f"✅ Email sent successfully to {payload['recipient']}")
        else:
            print(f"❌ Email failed to send to {payload['recipient']}")

    except Exception as e:
        print(f"❌ Failed to send email to {payload['recipient']}: {e}")


def mark_as_sent(supabase: Client, email_id: int):
    # Fetch the email record to get its details
    response = supabase.table("scheduled-emails").select("sender_name,recipient,body_text,scheduled_time,mailbox").eq("id", email_id).single().execute()
    record = response.data

    if record:
        # Insert into sent-emails table
        supabase.table("sent-emails").insert({
            "name": record.get("sender_name"),
            "email": record.get("recipient"),
            "sent_at":record.get("scheduled_time"),
            "body_text": record.get("body_text"),
            "mailbox": record.get("mailbox")
        }).execute()
        supabase.table("scheduled-emails").delete().eq("id", email_id).execute()

def main():
    scheduled_emails = fetch_scheduled_emails(supabase_client)

    if not scheduled_emails:
        print("No scheduled emails at this time.")
        return

    for record in scheduled_emails:
        send_email(record)
        # print(f"Attempting to send email to {record.get('recipient')} scheduled at {record.get('scheduled_time')}")
        # random delay between 4–8 seconds
        delay = random.uniform(4, 8)
        print(f"⏳ Sleeping for {delay:.2f} seconds before next email...")
        time.sleep(delay)
        
main()
