import sys
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        Stealth().apply_stealth_sync(context)
        page = context.new_page()
        page.goto("https://www.coupang.com/np/categories/305798?page=2", wait_until="networkidle")
        html = page.content()
        with open("playwright_page2.html", "w", encoding="utf-8") as f:
            f.write(html)
        browser.close()

if __name__ == "__main__":
    main()
