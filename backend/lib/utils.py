from playwright.sync_api import sync_playwright
import time
from html_to_markdown import convert_to_markdown
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from strip_markdown import strip_markdown
from typing import Dict, List
from apify_client import ApifyClient
import json
load_dotenv()

intelligence=os.getenv("OPEN_AI_API_KEY")
apify_token = os.getenv("APIFY_TOKEN")
client = OpenAI(api_key=intelligence)
apify_client = ApifyClient(apify_token)

class Custom_Email(BaseModel):
    email:str
    subject:str

def extract_linkedin_posts(url:str) -> str:
    post_limit = 4
    linkedin_profiles = [url]
    linkedin_json = {
        "deepScrape": False,
        "limitPerSource": 3,
        "rawData": False,
        "urls": [
            url
        ]
    }
    actor_run = apify_client.actor('supreme_coder/linkedin-post').call(
        run_input=linkedin_json
    )
    dataset_items = apify_client.dataset(actor_run['defaultDatasetId']).list_items().items
    posts = list(map(lambda x: x["text"],dataset_items))
    return posts
     
def extract_info_from_website(url:str) -> str:
    max_tokens_per_page = 100000
    dossier = ""
    summarry_prompt = """
        Use the markdown from the website below and write me a detailed description of what the business is about. 
        Here's the content of a website. Give me as much detail as possible.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, timeout=60000, )
        page = browser.new_page()
        page.goto(url)
        page_url = page.url
        if(page_url.endswith("/")):
                page_url = page_url[:-1]
                print("Formated Url without / -->", page_url)
        body_html = page.query_selector("body").inner_html()
        markdowns = [convert_to_markdown(body_html)]
        for markdown_text in markdowns:
            plain_text = strip_markdown(markdown_text)

            if((len(plain_text)/4) > max_tokens_per_page): 
                print("Too expensive to scrape")
                return
            response = client.responses.create(
                model="gpt-5-nano",
                input=f"""
                    {summarry_prompt}
                    ---------------------------------
                    {plain_text}
                """
            )
            dossier = response.output_text
        browser.close()    
    return dossier

def generateCustomEmail(dossier: List[Dict[str, str]]) -> Dict[str, str]:
    prompt = f"""
        We just scraped a series of web pages for a business called {dossier[0]["company"]}. 
        And the decision maker  {dossier[0]["decision_maker"]} who is holding the position of {dossier[0]["job_title"]}.

        Your task is to take the information we have scraped about them from their linkedIn and website.
        and turn them into a personalized email for a cold email campaign.
        We want to use this data to craft a super personalised email so that it looks like we did an in depth research into them .

        You'll return the email in the following JSON format:
        "email":Hey [decision maker's name], Love [thing]—also a fan of [otherThing]. This might be a long shot, but I figured I’d reach out anyway. I’ve been checking out your site and LinkedIn over the past couple weeks and thought something I built could actually help you guys. To put it bluntly, it’s a tool that auto-generates a detailed SEO audit PDF for any website. It only costs a few cents to run, converts really well, and since [business-name] is mainly focused on SEO, it feels like a solid fit. And just so you know, this isn’t some automated blast, I’m a real person. I even recorded a quick video running an audit on your very own site (and introducing myself), so you can see this isn’t coming from a software list., "subject":"Could this work for you too? "
        Rules:
        Write in a spartan/laconic tone of voice.
        Make sure to use the above format when constructing email. You are only really filling out the variable based on the info, keep the rest the same. We wrote it this way on purpose.
        Shorten the company name wherever possible (say, “XYZ” instead of “XYZ Agency”). 
        More examples: “Love AMS” instead of “Love AMS Professional Services”, “Love Mayo” instead of “Love Mayo Inc.”, etc.
        Do the same with locations. “San Fran” instead of “San Francisco”, “BC” instead of “British Columbia”, etc.
        For your variables, focus on small, non-obvious things to paraphrase. The idea is to make people think we really looked deep into their website, so don’t use something obvious. Do not say cookie-cutter stuff like “Love your orientation”, “Love your marketing”, etc.

        -----------------------------------------------------------------------------------------------
        Here's the business information taken from the website:
        {dossier[0]["website_content"]}
        ------------------------------------------------------------------------------------------------
         Here are some posts from LinkedIn:
         {dossier[0]["linkedin"]}
    """
    system_prompt = """
        You are an expert cold email personalization assistant.  
        Your job is to take dossier of a company and generate persoanlized emails for a cold email campaign.  

        ### Output Format:
        - Always return your response as valid JSON.
        - Use the exact structure: {"email":"...", "subject":"...."}  
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
        5. No extra line breaks or "\n\n".  

        ### Example:
        Input (summary):  
        "Aina runs Maki, an SEO agency focused on helping Local Businesses rank on google maps"  

        Output (JSON only):  
        {"email":"Hey Maki, Love love what you're doing at Maki. I noticed your focus on SEO. which tells me ranking is a big deal for you guys. This might be a long shot, but I figured I’d reach out anyway. I’ve been checking out your site and LinkedIn over the past couple weeks and thought something I built could actually help you guys. To put it bluntly, it’s a tool that auto-generates a detailed SEO audit PDF for any website. It only costs a few cents to run, converts really well, and since Maki is mainly focused on SEO, it feels like a solid fit. And just so you know, this isn’t some automated blast, I’m a real person. I even recorded a quick video running an audit on your very own site (and introducing myself), so you can see this isn’t coming from a software list.", subject:"Could this work for you too Maki?"}    
    """
    response = client.responses.parse(
        model="gpt-5-nano",
        input=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        text_format=Custom_Email
    )
    return response.output_parsed


website =extract_info_from_website("http://www.coloradoseoservices.net",)
posts = extract_linkedin_posts("http://www.linkedin.com/in/lou-aleman-79514910")
email = generateCustomEmail([{"decision_maker":"Lou Aleman", "company":"Colorado SEO Services","job_title":"CEO", "website_content":website,"linkedin":posts}])
print("Final Email", email)