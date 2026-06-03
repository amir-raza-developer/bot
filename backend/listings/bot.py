# SMBot - bot.py (Playwright)
from playwright.sync_api import sync_playwright
import random

def run_bot(email, password):
    """Standalone bot entry point."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--start-maximized","--no-sandbox"])
            ctx  = browser.new_context(viewport={"width": 1366, "height": 768})
            page = ctx.new_page()
            page.goto("https://www.facebook.com/login", wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            page.fill("#email", email)
            page.wait_for_timeout(400)
            page.fill("#pass", password)
            page.wait_for_timeout(400)
            page.click("[name='login']")
            page.wait_for_timeout(5000)
            print("✅ Logged in.")
            input("Press Enter to close...")
            browser.close()
        return "Bot completed"
    except Exception as e:
        return f"Bot error: {e}"
