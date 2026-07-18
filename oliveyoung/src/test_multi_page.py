"""
메인 페이지 세션 생성 후 동일 세션에서 pageIdx 파라미터를 변경하여 2페이지로 직접 이동이 가능한지 테스트하는 스크립트입니다.
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def test_pages():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. 메인 페이지 방문
        print("1. 메인 홈 방문...")
        await page.goto("https://www.oliveyoung.co.kr/", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # 2. 자바스크립트를 이용해 영양제 1페이지로 전환
        print("2. 1페이지로 전이...")
        js_code = "common.link.moveCategory('100000200010025', 'Cat100000200010025_MID', 'Drawer');"
        await page.evaluate(js_code)
        await page.wait_for_selector("ul.cate_prd_list", timeout=30000)
        print("1페이지 로딩 완료.")
        
        # 3. 동일 세션에서 URL을 강제로 2페이지로 변경하여 page.goto 테스트
        target_url_p2 = "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000200010025&fltDispCatNo=&prdSort=01&pageIdx=2&rowsPerPage=24"
        print(f"3. 동일 세션에서 2페이지 직접 이동 시도: {target_url_p2}")
        await page.goto(target_url_p2, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        title = await page.title()
        print("2페이지 타이틀:", title)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        products = soup.select("ul.cate_prd_list > li")
        print(f"2페이지에서 파싱된 상품 수: {len(products)}")
        
        if len(products) > 0:
            first_prd_name = products[0].select_one(".tx_name")
            print("2페이지 첫번째 상품명:", first_prd_name.get_text(strip=True) if first_prd_name else "N/A")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_pages())
