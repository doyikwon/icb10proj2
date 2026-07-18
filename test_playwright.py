from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

def test_coupang():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # 헤드리스 모드 False로 하면 감지 우회에 도움됨
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        )
        Stealth().apply_stealth_sync(context)
        page = context.new_page()
        
        print("Navigating to page 1...")
        page.goto("https://www.coupang.com/np/categories/305798?page=1", wait_until="networkidle")
        time.sleep(3)
        print("Page 1 Title:", page.title())
        
        print("Navigating to page 2...")
        page.goto("https://www.coupang.com/np/categories/305798?page=2", wait_until="networkidle")
        time.sleep(3)
        print("Page 2 Title:", page.title())
        
        browser.close()

if __name__ == "__main__":
    test_coupang()
