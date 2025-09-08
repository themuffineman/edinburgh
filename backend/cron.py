import os
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
from lib import email


# Load your Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_scheduled_emails(supabase: Client):
    # Current time (UTC, to the minute)
    current_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)

    # Define a 10-minute window around current time
    window_start = current_time - timedelta(minutes=5)
    window_end = current_time + timedelta(minutes=5)

    # Query rows within the time window
    response = (
        supabase.table("scheduled-emails")
        .select("*")
        .gte("scheduled_time", window_start.isoformat())
        .lte("scheduled_time", window_end.isoformat())
        .execute()
    )

    return response.data or []

def send_email(record):
    try:
        payload = {
            "recipient": record.get("recipient"),
            "subject": record.get("subject", "No Subject"),
            "body": record.get("body_text", "No Content"),
            "sender_name": record.get("sender_name", "No Content")
        }
        success, error_message = email.send_email(
            to_address=payload["recipient"],
            subject=payload["subject"],
            body_text=payload["body"],
            sender_name=payload["sender_name"]
        )
        if success:
            print(f"✅ Email sent successfully to {payload['recipient']}")
        else:
            print(f"❌ Email failed to send to {payload['recipient']}")

    except Exception as e:
        print(f"❌ Failed to send email to {payload['recipient']}: {e}")



def main():
    supabase = get_supabase_client()
    scheduled_emails = fetch_scheduled_emails(supabase)

    if not scheduled_emails:
        print("No scheduled emails at this time.")
        return

    for record in scheduled_emails:
        send_email(record)

if __name__ == "__main__":
    main()
