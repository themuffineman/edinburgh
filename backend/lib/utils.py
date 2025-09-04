from playwright.sync_api import sync_playwright
import time
from html_to_markdown import convert_to_markdown
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
intelligence=os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=intelligence)


def extract_info_from_website(url:str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, timeout=60000)
        page = browser.new_page()
        page.goto(url)
        body_html = page.query_selector("body").inner_html()
        markdown = convert_to_markdown(body_html)
        plain_text = re.sub(r'[*_`#>-]', '', markdown)
        response = client.responses.create(
            model="gpt-5",
            input=f"""
                Summarize this website markdown into a usable description:
                {plain_text}
            """
        )
        print("Summary is: ", response.output_text)
        browser.close()
extract_info_from_website("https://looca.app")
