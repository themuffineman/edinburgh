from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
from openai import OpenAI
from playwright.async_api import async_playwright, Browser, Playwright
import time
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
    linkedin_url: str
    website_url: str

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
async def extract_info_from_website(url: str, browser: Browser) -> Optional[str]:
    """Scrapes a website using a pre-initialized browser and returns a summary."""
    max_tokens_per_page = 100000
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
        markdown_text = convert_to_markdown(html_raw)
        plain_text = strip_markdown(markdown_text)

        if (len(plain_text) / 4) > max_tokens_per_page:
            print("Website content too large to summarize.")
            await page.close()  # Close the page, not the browser
            return None

        # response = client.responses.create(
        #     model="gpt-5-nano",
        #     input=f"{summary_prompt}\n---------------------------------\n{plain_text}"
        # )
        dossier = plain_text #response.output_text
        await page.close() # Close the page after use
        return dossier
    except Exception as e:
        print(f"Error extracting website info: {e}")
        return None
def generateCustomEmail(dossier: Dict) -> Custom_Email:
    """Generates a personalized email and subject line using a language model."""
    prompt = f"""
        We just scraped a series of web pages for a business called {dossier["company_name"]}.
        And the decision maker is {dossier["decision_maker_name"]} who is holding the position of {dossier["decision_maker_title"]}.

        Your task is to take the information we have scraped about them from their LinkedIn and website
        and turn it into a personalized email for a cold email campaign.
        We want to use this data to craft a super personalized email so that it looks like we did an in-depth research into them.

        You'll return the email in the following JSON format:
        "email":"Hey [decision maker's name], [compliment]. This might be a long shot, but I figured I’d reach out anyway. I’ve been checking out your site and LinkedIn over the past couple weeks and thought something I built could actually help you guys. To put it bluntly, it’s a tool that auto-generates a detailed SEO audit PDF for any website. It only costs a few cents to run, converts really well, and since [business-name] is mainly focused on SEO, it feels like a solid fit. And just so you know, this isn’t some automated blast, I’m a real person. I even recorded a quick video running an audit on your very own site (and introducing myself), so you can see this isn’t coming from a software list.", "subject":"Could this work for you too [decision maker name]?"
        Rules:
        Write in a spartan/laconic tone of voice.
        Make sure to use the above format when constructing the email. We wrote it this way on purpose. When know what works. Stick to the format!
        Shorten the company name wherever possible (say, “XYZ” instead of “XYZ Agency”).
        More examples: “Love AMS” instead of “Love AMS Professional Services”, “Love Mayo” instead of “Love Mayo Inc.”, etc.
        Do the same with locations. “San Fran” instead of “San Francisco”, “BC” instead of “British Columbia”, etc.
        For your variables, focus on small, non-obvious things to paraphrase. The idea is to make people think we really looked deep into their website, so don’t use something obvious. Do not say cookie-cutter stuff like “Love your orientation”, “Love your marketing”, etc.

        -----------------------------------------------------------------------------------------------
        Here's the business information taken from the website:
        {dossier["website_content"]}
        ------------------------------------------------------------------------------------------------
        Here are some posts from LinkedIn:
        {dossier["linkedin"]}
    """
    system_prompt = """
        You are an expert cold email personalization assistant.
        Your job is to take a dossier of a company and generate personalized emails for a cold email campaign.

        ### Output Format:
        - Always return your response as valid JSON.
        - Use the exact structure: {"body":"...", "subject":"...."}
        - Do not include explanations, comments, or extra text. JSON only.

        ### Writing Style:
        - Spartan, laconic, professional tone.
        - Make it feel like we *really looked into their website*.
        - Use the list of compliments provided. Again stick to them do not change or deviate from them. But you're free to edit slightly to make sure they fit the context of the dossier
        - Mention something small, specific, and non-obvious (not mission statements or generic compliments).
        - Avoid cookie-cutter phrases like "Love your orientation" or "Great marketing content."

        ### List of Compliments To Use
        - There’s something about the way your team approaches SEO that makes me genuinely excited to learn from it.
        - I might have spent way too much time reading your recent SEO posts… they're very insightful.
        - Honestly, I’ve had a tab open on your linkedIn/site for days… the stuff you put out on SEO is very insightful .
        - Your team’s creativity in SEO is the kind that makes me rethink my entire approach.
        - I’ve read your latest SEO guide three times… just to make sure I didn’t miss anything.
        - I love how your SEO work somehow manages to be both ambitious and ridiculously practical.
        - There’s something about the way your team approaches SEO that makes me genuinely excited to learn from it.
        - Really love the work you've been doing on SEO with [business name], I've been secretly cheering from the sidelines.
        - I really admire the creativity [company] brings to the SEO space.
        - I’ve been following [company]’s work in SEO, it’s honestly inspiring.
        ### Rules:
        1. Shorten company names ("XYZ" instead of "XYZ Agency").
        2. Shorten location names ("San Fran" instead of "San Francisco").
        3. Tie the detail you found back to how our outreach system could help.
        4. Keep it natural, not robotic.
        5. No extra line breaks or "\\n\\n".

        ### Example:
        Input (summary):
        "Aina runs Maki, an SEO agency focused on helping Local Businesses rank on google maps"

        Output (JSON only):
        {"body":"Hey Darren, Love your breakdown on local SEO, also enjoyed your guide on boosting local search traffic. This might be a long shot, but I figured I’d reach out anyway. I’ve been checking out your site and LinkedIn over the past couple weeks and thought something I built could actually help you guys. To put it bluntly, it’s a tool that auto-generates a detailed SEO audit PDF for any website. It only costs a few cents to run, converts really well, and since [business-name] is mainly focused on SEO, it feels like a solid fit. And just so you know, this isn’t some automated blast, I’m a real person. I even recorded a quick video running an audit on your very own site (and introducing myself), so you can see this isn’t coming from a software list.", "subject":"Could this work for you too Maki?"}
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

@app.post("/generate-email", response_model=Custom_Email)
async def generate_personalized_email(request_data: EmailRequest):
    """
    Generates a personalized cold email based on company and decision maker information.
    """
    try:
        print("Received Request: ",datetime.now())
        # 1. Scrape Website
        website_content = await extract_info_from_website(request_data.website_url, browser_instance)
        if not website_content:
            raise HTTPException(status_code=500, detail="Could not scrape or summarize website content.")

        # 2. Scrape LinkedIn
        linkedin_posts = extract_linkedin_posts(request_data.linkedin_url)
        # Note: LinkedIn scraping can sometimes fail, so we'll pass an empty list if there's no data.

        # 3. Create Dossier
        dossier = {
            "company_name": request_data.company_name,
            "decision_maker_name": request_data.decision_maker_name,
            "decision_maker_title": request_data.decision_maker_title,
            "website_content": website_content,
            "linkedin": linkedin_posts
        }

        # 4. Generate Email
        final_email = generateCustomEmail(dossier)
        return final_email

    except HTTPException as e:
        # Re-raise explicit HTTP exceptions
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during email generation.")