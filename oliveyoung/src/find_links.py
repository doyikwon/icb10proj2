"""
올리브영 메인 페이지의 HTML을 분석하여 영양제 카테고리(dispCatNo=100000200010025)로 바로 이동할 수 있는 GNB 내의 올바른 링크 구조를 탐색하는 스크립트입니다.
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def find_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("올리브영 메인 페이지 접속 중...")
        await page.goto("https://www.oliveyoung.co.kr/", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # 100000200010025 키워드가 들어있는 모든 링크 탐색
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if '100000200010025' in href or '건강식품' in text or '영양제' in text:
                links.append((text, href))
                
        print(f"\n발견된 관련 링크 수: {len(links)}")
        for idx, (txt, href) in enumerate(links):
            print(f"[{idx+1}] Text: {txt} | Href: {href}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_links())
