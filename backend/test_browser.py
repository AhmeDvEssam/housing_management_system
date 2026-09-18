import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to login page...")
        await page.goto("http://127.0.0.1:8000/admin/")
        
        await page.fill("input[name='username']", "admin")
        await page.fill("input[name='password']", "1")
        await page.press("input[name='password']", "Enter")
        
        print("Waiting for login to complete...")
        await page.wait_for_load_state('networkidle')
        
        print("Navigating to Add Booking page...")
        await page.goto("http://127.0.0.1:8000/admin/bookings/booking/add/")
        await page.wait_for_load_state('networkidle')
        
        print("Clicking select2 via JS...")
        await page.evaluate('''
            window.$('#id_member').select2('open');
        ''')
        await page.wait_for_timeout(1000)
        
        print("Taking screenshot...")
        screenshot_path = r"C:\Users\ahmed\.gemini\antigravity\brain\c5fd6d3e-2096-410a-aeb6-38895d76eb60\debug_screenshot.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print("Screenshot saved to", screenshot_path)
        
        await browser.close()
        return
        
        debug_log = await page.evaluate("document.querySelector('#v5-debug-log') ? document.querySelector('#v5-debug-log').innerText : 'NO DEBUG LOG FOUND'")
        with open("d:/housing/backend/debug_log.txt", "w", encoding="utf-8") as f:
            f.write(debug_log)
        
        await browser.close()
        return
        await page.wait_for_timeout(500)
        await page.keyboard.press("Enter")
        
        print("Member selected! Waiting 2 seconds for JS to process...")
        await page.wait_for_timeout(2000)
        
        print("Taking screenshot...")
        screenshot_path = r"C:\Users\ahmed\.gemini\antigravity\brain\c5fd6d3e-2096-410a-aeb6-38895d76eb60\debug_screenshot.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print("Screenshot saved to", screenshot_path)
        
        # Check values
        id_no = await page.evaluate("document.getElementById('id_guest_id_no') ? document.getElementById('id_guest_id_no').value : 'null'")
        name = await page.evaluate("document.getElementById('id_guest_name') ? document.getElementById('id_guest_name').value : 'null'")
        
        print(f"RESULTS: ID No: '{id_no}', Name: '{name}'")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
