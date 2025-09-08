from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import List, Optional
from openai import OpenAI
from playwright.async_api import async_playwright, Browser, Playwright
from html_to_markdown import convert_to_markdown
import re
from apify_client import ApifyClient
from strip_markdown import strip_markdown
from datetime import datetime
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()
print("\033[1;32;40mA PENDORIAN PRODUCTION\033[0m")

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
# --- Startup and Shutdown Events for Resource Management ---

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

class EmailRequest(BaseModel):
    company_name: str
    decision_maker_name: str
    decision_maker_title: str
    website_url: str
    website_content:str
    is_qualified:bool

# --- Your Existing Functions (Modified for server context) ---
def extract_linkedin_posts(url: str) -> List[str]:
    """Extracts recent posts from a LinkedIn profile URL using Apify."""
    print(f"Extracting LinkedIn posts from: {url}")
    try:
        linkedin_json = {
            "deepScrape": False,
            "limitPerSource": 3,
            "rawData": False,
            "urls": [url]
        }
        actor_run = apify_client.actor('supreme_coder/linkedin-post').call(
            run_input=linkedin_json
        )
        dataset_items = apify_client.dataset(actor_run['defaultDatasetId']).list_items().items
        posts = list(map(lambda x: x["text"], dataset_items))
        return posts
    except Exception as e:
        print(f"Error extracting LinkedIn posts: {e}")
        return []
async def extract_info_from_website(url: str, browser: Browser):
    """Scrapes a website using a pre-initialized browser and returns a summary."""
    max_tokens_per_page = 100000
    is_qualified=False
    summary_prompt = """
        Use the markdown from the website below and write me a detailed description of what the business is about.
        Here's the content of a website. Give me as much detail as possible.
    """
    print(f"Extracting website info from: {url}")
    try:
        # We get a new page from the existing browser instance
        page = await browser.new_page()
        await page.goto(url)
        body_html = await page.query_selector("body")
        html_raw = await body_html.inner_html()
        markdown_text:str = convert_to_markdown(html_raw)
        plain_text:str = strip_markdown(markdown_text)

        if (len(plain_text) / 4) > max_tokens_per_page:
            print("Website content too large to summarize.")
            await page.close()  # Close the page, not the browser
            return None
        if("audit" in plain_text):
            is_qualified = True
        dossier = plain_text
        await page.close() # Close the page after use
        return {"dossier":dossier, "is_qualified":is_qualified}
    except Exception as e:
        print(f"Error extracting website info: {e}")
        return None
def generateCustomEmail(dossier:  dict[str, any]) -> Custom_Email:
    """Generates a personalized email and subject line using a language model."""
    
    # when_you_enable_recording_add_this = "And just so you know, this isn’t some automated blast, I’m a real person. I recorded a quick video running an audit on your very own site."
    example_response= f""" "body":"Hey [decision maker name],\n \nSaw the [something that stood out their website regarding their business service, operation or some stand out way they did something] on [business name]'s site other day, it a nice touch, hadn’t seen anyone [frame it/say it/present it/showcase it] it that way before.\n \nSo this might be a long shot, but I figured I’d reach out anyway. I built a tool that auto-generates a detailed SEO audit for any website you enter. { "It costs just a few cents to run, and I can see it easily doubling your conversion into paid clients with this as a lead magnet." if dossier["is_qualified"] == False else "It only costs a few cents to run. Since it runs almost instantly, you can free up your team to take on more clients."}\n \n{"I could build this for you up-front at no cost, and the best part is if it doesn’t increase conversions by at least 50%, you don’t pay. I can get back to you in 1hr with a link to the system." if dossier["is_qualified"] == False else "I could do this up-front at no cost and if you like it, we could work together longer term. Assuming you're in I’ll get back to you in 30 mins or so with a link to the system."} Do you want me to just go ahead and do it ?\n \nLooking forward to hearing from you [deicsion maker name], \nPetrus", "subject":"Could this work for you too [decision maker name]?" """

    example_output= f""" "body":"Hey Darren,\n \nI came across the SEO 5280 mention on Maki's site the other day hadn’t seen it phrased like that before, nice touch.\n \nSo this might be a long shot, but I figured I’d reach out anyway. I built a tool that auto-generates a detailed SEO audit for any website you enter. {"It costs just a few cents to run, and I can see it easily doubling your conversion into paid clients with this as a lead magnet." if dossier["is_qualified"] == False else "It only costs a few cents to run. Since it runs almost instantly, you can free up your team to take on more clients."}\n \n{"I could build this for you up-front at no cost, and the best part is if it doesn’t increase conversions by at least 50%, you don’t pay. I can get back to you in 1hr with a link to the system" if dossier["is_qualified"] == False else "I could do this up-front at no cost and if you like it, we could work together longer term. Assuming you're in I’ll get back to you in 30 mins or so with a link to the system."} I can get back to you in 1hr with a link to the system. Do you want me to just go ahead and do it?\n \nLooking forward to hearing from you Darren, \nPetrus", "subject":"Could this work for you too Darren?"" """

    prompt = f"""
        We just scraped a series of web pages for a business called {dossier['company_name']}.
        And the decision maker is {dossier['decision_maker_name']} who is holding the position of {dossier['decision_maker_title']}.
        Use commas instead of em dashes. No em dashes. No em dashes use commas instead
        I repeat use commas instead of em dashes. Please I beg you, no em dashes. This is life or death.
        Comply to rules, comply to the rules.

        Your task is to take the information we have scraped about them from their LinkedIn and website
        and turn it into a personalized email for a cold email campaign.
        We want to use this data to craft a super personalized email so that it looks like we did an in-depth research into them.

        You'll return the email in the following JSON format:
        {{ {example_response} }}
        Rules:
        Write in a spartan/laconic tone of voice.
        Make sure to use the above format when constructing the email. We wrote it this way on purpose. When know what works. Stick to the format!
        Do not add any extra paragrpahs, case studies or "postscriptum" in the email. Your role here is mostly to fill in the variables to make it more human friendly.
        Do not add you own twist or anything that is not specified in the format. The format is King. I have refined and perfected over years of cold emailing. It's perfect.
        Make sure the punctuations are correct.
        Shorten the company name wherever possible (say, “XYZ” instead of “XYZ Agency”).
        More examples: “Love AMS” instead of “Love AMS Professional Services”, “Love Mayo” instead of “Love Mayo Inc.”, etc.
        Do the same with locations. “San Fran” instead of “San Francisco”, “BC” instead of “British Columbia”, etc.
        For your variables, focus on small, non-obvious things to paraphrase. The idea is to make people think we really looked deep into their website, so don’t use something obvious. Do not say cookie-cutter stuff like “Love your orientation”, “Love your marketing”, etc.

        -----------------------------------------------------------------------------------------------
        Here's the business information taken from the website:
        {dossier["website_content"]}
    """
    
    system_prompt = f"""
        You are an expert cold email personalization assistant.
        Your job is to take a dossier of a company and generate personalized emails for a cold email campaign.

        ### Output Format:
        - Always return your response as valid JSON.
        - Use the exact structure: {{ "body":"...", "subject":"...." }}
        - Do not include explanations, comments, or extra text. JSON only.

        ### Writing Style:
        - Spartan, laconic, professional tone.
        - Make it feel like we *really looked into their website*.
        - Mention something small, specific, and non-obvious (not mission statements or generic compliments).
        - Avoid cookie-cutter phrases like "Love your orientation" or "Great marketing content."

        ### Rules:
        1. Shorten company names ("XYZ" instead of "XYZ Agency").
        2. Shorten location names ("San Fran" instead of "San Francisco").
        3. Tie the detail you found back to how our outreach system could help.
        4. Keep it natural, not robotic.
        5. Add extra line breaks "\\n\\n" to split different sentences and make the email more readable. Make sure they're placed in appropriate places at your own discretion.
        6. Make sure you add the appropriate punctuations at your own descretion.

        ### Example:
        Input (summary):
        "Darren runs Maki, an SEO agency focused on helping Local Businesses rank on google maps"

        Output (JSON only):
        {{ {example_output} }}
    """
    try:
        response = client.responses.parse(
            model="gpt-5-nano", 
            text_format=Custom_Email,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
        )
        email_data = response.output_parsed
        return email_data
    except Exception as e:
        print(f"Error generating custom email: {e}")
        raise HTTPException(status_code=500, detail="Error generating custom email. Please check the AI models and prompts.")

# --- API Endpoint ---
