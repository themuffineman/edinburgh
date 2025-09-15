
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import List, Optional
from openai import OpenAI
from playwright.async_api import async_playwright, Browser, Playwright
import re

playwright_instance: Optional[Playwright] = None
browser_instance: Optional[Browser] = None

async def check_new_emails(email: str, password: str) -> List[str]:
    global playwright_instance, browser_instance
    if playwright_instance is None or browser_instance is None:
        playwright_instance = await async_playwright().start()
        browser_instance = await playwright_instance.chromium.launch(headless=True)
    
    context = await browser_instance.new_context()
    page = await context.new_page()
    
    try:
        await page.goto("https://mail.hostinger.com/")
        
        # Login
        await page.fill('input#rcmloginuser', email)
        await page.click('button:has-text("Next")')
        await page.wait_for_timeout(2000)  # Wait for password field to appear
        await page.fill('input#rcmloginpwd', password)
        await page.click('button#rcmloginsubmit')
        
        # Wait for inbox to load
        await page.wait_for_selector('div#taskmenu', timeout=15000)
        await page.wait_for_selector('a[rel="INBOX"]', timeout=15000)
        #Wait for new message counter number
        new_messages_count= await page.wait_for_selector('a[rel="INBOX"] > span', timeout=15000)
        if new_messages_count:
          print(f"New messages count: {await new_messages_count.text_content()}")
        else:
          print("No new messages found.")  
        # Extract email subjects
    except Exception as e:
        print(f"Error checking emails: {e}")
        return []
    finally:
        await context.close()