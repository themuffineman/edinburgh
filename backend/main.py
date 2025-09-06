from fastapi import FastAPI, HTTPException
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
from lib import email,dossier

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
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://127.0.0.1:65506", 
    "*"
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
    recipients: List[str]
    subject: str
    html_content: str
    sender_name: str
class Email_Sending_Response(BaseModel):
    message:str
    successful_recipients:list
# --- API Endpoints ---

@app.post("/generate-email", response_model=Custom_Email)
async def generate_personalized_email(request_data: Email_Request):
    """
    Generates a personalized cold email based on company and decision maker information.
    """
    try:
        print("Received Request: ",datetime.now())
        # 1. Scrape Website
        website_content = await dossier.extract_info_from_website(request_data.website_url, browser_instance)
        if not website_content:
            raise HTTPException(status_code=500, detail="Could not scrape or summarize website content.")

        # 2. Scrape LinkedIn
        linkedin_posts = dossier.extract_linkedin_posts(request_data.linkedin_url)
        # Note: LinkedIn scraping can sometimes fail, so we'll pass an empty list if there's no data.

        # 3. Create Dossier
        lead_dossier = {
            "company_name": request_data.company_name,
            "decision_maker_name": request_data.decision_maker_name,
            "decision_maker_title": request_data.decision_maker_title,
            "website_content": website_content,
            "linkedin": linkedin_posts
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
@app.post("/send-email", response_model=Email_Sending_Request)
def send_emails_endpoint(request: Email_Sending_Request):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise HTTPException(status_code=500, detail="Email address or password environment variables not set.")

    successful_sends = []
    failed_sends = {}
    
    for recipient in request.recipients:
        success, error_message = email.send_email(
            to_address=recipient,
            subject=request.subject,
            html_content=request.html_content,
            sender_name=request.sender_name
        )
        if success:
            successful_sends.append(recipient)
        else:
            failed_sends[recipient] = error_message
        
        # Add a delay between emails to avoid rate-limiting
        delay = random.randint(30, 120)
        print(f"Waiting {delay} seconds before next email...")
        time.sleep(delay)

    if failed_sends:
        raise HTTPException(status_code=500, detail={
            "message": "Some emails failed to send.",
            "successful": successful_sends,
            "failed": failed_sends
        })

    return {"message": "All emails sent successfully.", "successful_recipients": successful_sends}
