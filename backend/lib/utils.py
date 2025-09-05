from playwright.sync_api import sync_playwright
import time
from html_to_markdown import convert_to_markdown
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import json


load_dotenv()
intelligence=os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=intelligence)
class IdealUrls(BaseModel):
    urls: list[str]


def extract_info_from_website(url:str) -> str:

        summarry_prompt = """
            Use the makrdown from the website below and write me a description of what the business is about. 
            Here's the content of a website. 
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, timeout=60000)
            page = browser.new_page()
            page.goto(url)
            page_url = page.url
            if page_url.endswith("/"):
                page_url = page_url[:-1]
            print("page url is", page_url)
            body_html = page.query_selector("body").inner_html()
            a_tags = page.query_selector_all("a")
            hrefs = []
            for tag in a_tags:
                  hrefs.append(tag.get_attribute("href"))
            hrefs = [href for href in hrefs if "#" not in href or href.startswith("/") == False]
            hrefs = set(hrefs)
            hrefs = list(hrefs)

            ideal_urls_res = client.responses.parse(
                model="gpt-4.1-nano",
                input=[
                        {"role": "system", "content": "Extract the event information."},
                        {
                            "role": "user",
                            "content": f"""
                                        We are building a docier of this business by scraping someof their web pages.
                                        But of course manyof these are irrelavant and not valid to extract any meaningful data about the business
                                        like pivacy-policies, sitemaps. Filter this list of urls to include only the most high value page that we can extract 
                                        themost information from inorder to persoanlize our out reach 
                                        -------------------------------
                                        {hrefs}
                                    """,
                        },
                ],
                text_format=IdealUrls
            )
            ideal_urls:list[str] = json.loads(ideal_urls_res.output_text)
            for ideal_url in ideal_urls:
                page.goto(f"{page_url}{ideal_url}")




            browser.close()

            return
            markdown = convert_to_markdown(body_html)
            plain_text = re.sub(r'[*_`#>-]', '', markdown)
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
