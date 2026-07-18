"""
올리브영 페이지를 플레이라이트로 로드한 후 HTML 본문을 텍스트 파일로 저장하여 차단 여부와 페이지 내용을 직접 검증하는 스크립트입니다.
"""

import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        url = "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000200010025&fltDispCatNo=&prdSort=01&pageIdx=1&rowsPerPage=24"
        print(f"Navigating to: {url}")
        
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        title = await page.title()
        print(f"Page Title: {title}")
        
        content = await page.content()
        with open("oliveyoung/data/page_dump.html", "w", encoding="utf-8") as f:
            f.write(content)
            
        print("HTML Saved to oliveyoung/data/page_dump.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
