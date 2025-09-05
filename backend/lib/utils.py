from playwright.sync_api import sync_playwright
import time
from html_to_markdown import convert_to_markdown
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from strip_markdown import strip_markdown
import json


load_dotenv()
intelligence=os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=intelligence)
class IdealUrls(BaseModel):
    urls: list[str]


def extract_info_from_website(url:str) -> str:
        max_tokens_per_page = 100000
        summarry_prompt = """
            Use the makrdown from the website below and write me a description of what the business is about. 
            Here's the content of a website. 
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
                    model="gpt-4.1-nano",
                    input=f"""
                        {summarry_prompt}

                        ---------------------------------

                        {plain_text}
                    """
                )
                print("Summary is: ", response.output_text)
            browser.close()
extract_info_from_website("https://looca.app")
