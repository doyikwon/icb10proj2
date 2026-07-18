import time
from playwright.sync_api import sync_playwright

def test():
    url = "https://www.klook.com/ko/activity/7955-hanbok-rental-voucher-at-kyeonbokgung-store-in-hanboknam-seoul/"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(5)
        
        print("Title:", page.title())
        texts = page.locator('h1, p').all_inner_texts()
        print("Texts:", texts[:5])
        
        # Save screenshot for debugging
        page.screenshot(path="test_klook.png")
        
        browser.close()

if __name__ == "__main__":
    test()
