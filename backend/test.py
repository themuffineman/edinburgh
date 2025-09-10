import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
from supabase import create_client, Client
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Query rows within the time window
response = (
    supabase_client.table("scheduled-emails")
    .select("*")
    .eq("sent", True) 
    .execute()
)
print(response.data[0]["id"] or [])
# def mark_as_sent(supabase: Client, email_id: int):
#     supabase.table("scheduled-emails").update({"sent": True}).eq("id", email_id).execute()
# mark_as_sent(supabase_client,32)
