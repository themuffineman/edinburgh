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
import json
load_dotenv()
intelligence=os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=intelligence)
class Custom_Email(BaseModel):
    subject: str
    email:str


def extract_info_from_website(url:str, name:str) -> str:
        max_tokens_per_page = 100000
        dossier = []
        summarry_prompt = """
            Use the markdown from the website below and write me a detailed description of what the business is about. 
            Here's the content of a website. Give me as much detail as possible
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, timeout=60000, )
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
                print(plain_text)
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
                dossier.append({"name":name, "website_content":json.loads(response.output_text)})
            browser.close()
extract_info_from_website("https://looca.app", "Looca")


def generateCustomEmail(dossier: List[Dict[str, str]]) -> Dict[str, str]:
    prompt = f"""
        We just scraped a series of web pages for a business called {dossier[0]["name"]}. Your task is to take their summaries and turn them into catchy, personalized openers for a cold email campaign to imply that the rest of the campaign is personalized.
        You'll return your icebreakers in the following JSON format:
        "icebreaker":"Hey [name]. Love [thing]—also doing/like/a fan of [otherThing]. Wanted to run something by you (or hope you'll forgive me, but I creeped your site quite a bit, and know that [anotherThing] is important to you guys (or at least I'm assuming this given the focus on [fourthThing]). I put something together a few months ago that I think could help. To make a long story short, it's an outreach system that uses AI to find people hiring website devs. Then pitches them with templates (actually makes them a demo website). Costs just a few cents to run, very high converting, and I think it's in line with [someImpliedBeliefTheyHave]"
        Rules:
        Write in a spartan/laconic tone of voice.
        Make sure to use the above format when constructing your icebreakers. We wrote it this way on purpose.
        Shorten the company name wherever possible (say, “XYZ” instead of “XYZ Agency”). More examples: “Love AMS” instead of “Love AMS Professional Services”, “Love Mayo” instead of “Love Mayo Inc.”, etc.
        Do the same with locations. “San Fran” instead of “San Francisco”, “BC” instead of “British Columbia”, etc.
        For your variables, focus on small, non-obvious things to paraphrase. The idea is to make people think we really looked deep into their website, so don’t use something obvious. Do not say cookie-cutter stuff like “Love your orientation”, “Love your mission statement”, etc.

        -----------------------------------------------------------------------------------------------
        Here's the business information taken from the website:
        {dossier[0]["website_content"]}
    """
    system_prompt = """
        You are an expert cold email personalization assistant.  
        Your job is to take summaries of a company and generate ONE short, personalized icebreaker for a cold email campaign.  

        ### Output Format:
        - Always return your response as valid JSON.
        - Use the exact structure: {"icebreaker":"..."}  
        - Do not include explanations, comments, or extra text. JSON only.  

        ### Writing Style:
        - Spartan, laconic, professional tone.
        - Make it feel like we *really looked into their website*.  
        - Mention something small, specific, and non-obvious (not mission statements or generic compliments).  
        - Avoid cookie-cutter phrases like "Love your orientation" or "Great mission statement."  

        ### Rules:
        1. Shorten company names ("XYZ" instead of "XYZ Agency").  
        2. Shorten location names ("San Fran" instead of "San Francisco").  
        3. Tie the detail you found back to how our outreach system could help.  
        4. Keep it natural, not robotic.  
        5. No extra line breaks or "\n\n".  

        ### Example:
        Input (summary):  
        "Aina runs Maki, a dev agency focused on white-labelling and outsourcing."  

        Output (JSON only):  
        {"icebreaker":"Hey Aina, love what you're doing at Maki. I noticed your focus on white-labelling services, which tells me discretion is a big deal for you guys. I put something together that helps companies like yours scale outreach—AI finds people hiring website devs and pitches them with demo sites. Costs just a few cents to run, super high converting, and I think it fits with Maki’s emphasis on scalability."}    
    """
    response = client.responses.parse(
        model="gpt-5-nano",
        input={
            {
                "role": "system",
                "content": system_prompt
            },
            {"role": "user", "content": prompt},
        },
        text_format=Custom_Email,
    )
    return response.output_parsed

