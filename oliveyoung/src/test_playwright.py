"""
플레이라이트(Playwright)를 사용하여 올리브영 카테고리 페이지의 상품 정보를 추출하고 DOM 구조를 확인하는 스크립트입니다.
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
        print("Page loaded (DOM Content Loaded). Waiting 5 seconds for lazy loading...")
        await page.wait_for_timeout(5000)
        
        # 상품 아이템이 나타날 때까지 대기
        try:
            await page.wait_for_selector(".cate_prd_list, .prd_info", timeout=5000)
        except Exception as e:
            print("Selector timeout:", e)
        
        # 전체 HTML 길이 출력
        content = await page.content()
        print(f"HTML Content Length: {len(content)}")
        
        # 상품 정보 파싱 테스트
        items = await page.locator("div.prd_info").all()
        print(f"Found {len(items)} prd_info items.")
        
        for idx, item in enumerate(items[:5]):
            brand = await item.locator(".tx_brand").inner_text() if await item.locator(".tx_brand").count() > 0 else "N/A"
            name = await item.locator(".tx_name").inner_text() if await item.locator(".tx_name").count() > 0 else "N/A"
            cur_price = await item.locator(".prd_price .tx_cur").inner_text() if await item.locator(".prd_price .tx_cur").count() > 0 else "N/A"
            org_price = await item.locator(".prd_price .tx_org").inner_text() if await item.locator(".prd_price .tx_org").count() > 0 else "N/A"
            print(f"[{idx+1}] Brand: {brand} | Name: {name} | Price: {cur_price} (Org: {org_price})")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
