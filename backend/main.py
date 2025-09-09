from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import List, Optional
from openai import OpenAI
from playwright.async_api import async_playwright, Browser, Playwright
import time
import random
from apify_client import ApifyClient
from datetime import datetime
import asyncio
import sys
from lib import email,dossier,cron

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
print("\033[1;32;40mA PENDORIAN PRODUCTION\033[0m")
print("\033[1;32;40mA PENDORIAN PRODUCTION\033[0m")

# Load environment variables
load_dotenv()
# --- EMAIL CONFIG ---
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")
SENDER_NAME = os.getenv("SENDER_NAME")

# Initialize API clients from environment variables

openai_api_key = os.getenv("OPEN_AI_API_KEY")
apify_token = os.getenv("APIFY_TOKEN")
client = OpenAI(api_key=openai_api_key)
apify_client = ApifyClient(apify_token)

# --- FastAPI Setup ---
app = FastAPI(
    title="Email Personalization API",
    description="An API to generate personalized cold emails by scraping websites and LinkedIn.",
    version="1.0.0"
)
playwright_instance: Optional[Playwright] = None
browser_instance: Optional[Browser] = None
@app.on_event("startup")
async def startup_event():
    """
    Initializes the Playwright browser instance when the FastAPI app starts.
    """
    print("Starting up Playwright browser...")
    global playwright_instance, browser_instance
    playwright_instance = await async_playwright().start()
    browser_instance = await playwright_instance.chromium.launch(headless=True, timeout=60000)
    print("Playwright browser started.")
@app.on_event("shutdown")
async def shutdown_event():
    """
    Closes the Playwright browser instance when the FastAPI app shuts down.
    """
    print("Shutting down Playwright browser...")
    global browser_instance, playwright_instance
    if browser_instance:
        await browser_instance.close()
    if playwright_instance:
        await playwright_instance.stop()
    print("Playwright browser shut down.")

origins = [
    "https://edinburgh-nine.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Models ---

class Custom_Email(BaseModel):
    body: str
    subject: str

class Email_Request(BaseModel):
    company_name: str
    decision_maker_name: str
    decision_maker_title: str
    linkedin_url: str
    website_url: str
class Email_Sending_Request(BaseModel):
    recipient: str
    subject: str
    body_text: str
    sender_name: str
class Email_Sending_Response(BaseModel):
    message:str
    successful_recipients:list
class SuccessMessage(BaseModel):
    message: str
# --- API Endpoints ---

@app.post("/generate-email", response_model=Custom_Email)
async def generate_personalized_email(request_data: Email_Request):
    """
    Generates a personalized cold email based on company and decision maker information.
    """
    try:
        print("Received Generate Email Request: ",datetime.now())
        # 1. Scrape Website
        website_content = await dossier.extract_info_from_website(request_data.website_url, browser_instance)
        if not website_content["dossier"]:
            raise HTTPException(status_code=500, detail="Could not scrape or summarize website content.")

        # 2. Scrape LinkedIn
        # linkedin_posts = dossier.extract_linkedin_posts(request_data.linkedin_url)
        # Note: LinkedIn scraping can sometimes fail, so we'll pass an empty list if there's no data.

        # 3. Create Dossier
        lead_dossier = {
            "company_name": request_data.company_name,
            "decision_maker_name": request_data.decision_maker_name,
            "decision_maker_title": request_data.decision_maker_title,
            "website_content": website_content["dossier"],
            "is_qualified":website_content["is_qualified"]
        }
        # 4. Generate Email
        final_email = dossier.generateCustomEmail(lead_dossier)
        return final_email

    except HTTPException as e:
        # Re-raise explicit HTTP exceptions
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during email generation.")
@app.post("/send-email", response_model=Email_Sending_Response)
def send_emails_endpoint(request: Email_Sending_Request):
    print("Received Send Email Request: ",datetime.now())

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise HTTPException(status_code=500, detail="Email address or password environment variables not set.")

    successful_sends = []
    failed_sends = {}
    
    success, error_message = email.send_email(
        to_address=request["recipient"],
        subject=request.subject,
        body_text=request.body_text,
        sender_name=request.sender_name
    )
    if success:
        successful_sends.append(request["recipient"])
    else:
        failed_sends[request["recipient"]] = error_message
    
    # Add a delay between emails to avoid rate-limiting
    # delay = random.randint(30, 120)
    # print(f"Waiting {delay} seconds before next email...")
    # time.sleep(delay)

    # Notify me offline if this error occurs whatsapp perhaps
    if failed_sends:
        raise HTTPException(status_code=500, detail={
            "message": "Emails failed to send.",
            "successful": successful_sends,
            "failed": failed_sends
        })
    return {"message": "All emails sent successfully.", "successful_recipients": successful_sends}
@app.post("/send-scheduled-emails", response_model=SuccessMessage)
async def send_scheduled_emails(background_tasks: BackgroundTasks):
    """
    Triggers the sending of all scheduled emails as a background task.
    """
    background_tasks.add_task(cron.main)
    return {"message": "Scheduled emails task has been initiated."}
