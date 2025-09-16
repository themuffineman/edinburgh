
import os
from dotenv import load_dotenv
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Playwright
import re
import requests
import asyncio
import sys
load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

playwright_instance: Optional[Playwright] = None
browser_instance: Optional[Browser] = None
WEBHOOK_URL = os.getenv("WEBHOOK_URL_FOR_EMAIL_NOTIFY")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")
SENDER_EMAIL_1 = os.getenv("SENDER_EMAIL_1")
SENDER_EMAIL_2 = os.getenv("SENDER_EMAIL_2")
SENDER_EMAIL_3 = os.getenv("SENDER_EMAIL_3")
all_senders = [SENDER_EMAIL_1, SENDER_EMAIL_2, SENDER_EMAIL_3]

async def check_new_emails(email: str, password: str) -> List[str]:
    global playwright_instance, browser_instance
    if playwright_instance is None or browser_instance is None:
        playwright_instance = await async_playwright().start()
        browser_instance = await playwright_instance.chromium.launch(headless=False)
        print(f"Playwright browser for email checking started for: {email}.")
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
    viewport = {'width': 1920, 'height': 1080}
    storage_state = None 
    context = await browser_instance.new_context(
            user_agent=user_agent,
            viewport=viewport,
    )
    
    page = await context.new_page()
    
    try:
        await page.goto("https://mail.hostinger.com/")
        print("Navigated to email client webapp.")

        
        # Login
        await page.fill('input#rcmloginuser', email)
        await page.wait_for_timeout(4000)  # wait for 2 seconds
        await page.fill('input#rcmloginpwd', password)
        await page.click('button#rcmloginsubmit')
        
        # Wait for inbox to load
        await page.wait_for_selector('div#taskmenu', timeout=150000)
        await page.wait_for_selector('a[rel="INBOX"]', timeout=150000)
        #Wait for new message counter number
        new_messages_count= await page.wait_for_selector('a[rel="INBOX"] > span', timeout=15000)
        if new_messages_count:
            print(f"New messages count: {await new_messages_count.text_content()}")
            new_emails = await new_messages_count.text_content()
            data = {"email": f"from: {email} count:{new_emails}"}
            response = requests.post(WEBHOOK_URL, json=data)
            if response.status_code == 200:
                print("Data sent successfully.")
            else:
                print(f"Failed to send data. Status code: {response.status_code}")
        else:
          print("No new messages found.")  
    except Exception as e:
        print(f"Error checking emails: {e}")
        return []
    finally:
        await context.close()

if __name__ == "__main__":
    for sender in all_senders:
        if sender:
            asyncio.run(
                check_new_emails(sender, os.getenv("SENDER_PASSWORD"))
            )
# --- IGNORE ---