"""
올리브영 메인 페이지에서 시작하여 카테고리 메뉴를 클릭해 실제 영양제 페이지로 이동하고,
그 과정에서 변화하는 URL과 쿠키, DOM 구조를 탐색하는 진단 스크립트입니다.
"""

import asyncio
from playwright.async_api import async_playwright

async def explore():
    async with async_playwright() as p:
        print("헤드풀 모드로 브라우저 기동...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()
        
        print("메인 페이지 이동...")
        await page.goto("https://www.oliveyoung.co.kr/", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        print("카테고리 메뉴(카테고리 전체보기 또는 관련 메뉴) 탐색 및 클릭 시도...")
        # 올리브영 카테고리 전체보기 레이어 띄우기
        try:
            # 카테고리 레이어 버튼 클래스는 보통 'btn_menu' 또는 'menu' 관련 아이콘
            await page.click("#btnGnbOpen") # GNB 열기 버튼 클릭 시도 (ID가 btnGnbOpen일 확률이 높음)
            print("GNB 메뉴 버튼 클릭 성공.")
            await page.wait_for_timeout(1000)
            
            # 건강식품/영양제 카테고리 클릭
            # '건강식품' 텍스트를 가진 링크 클릭
            await page.click("text=건강식품")
            print("건강식품 대카테고리 클릭 성공.")
            await page.wait_for_timeout(2000)
            
            # 영양제 클릭
            await page.click("text=영양제")
            print("영양제 중카테고리 클릭 성공.")
            await page.wait_for_timeout(4000)
        except Exception as e:
            print("일반 클릭 실패, 대안 경로(직접 카테고리 뷰 링크 이동) 테스트:", e)
            # 건강식품 대카테고리 ID 또는 dispCatNo를 이용한 URL 이동
            # 영양제 전체 카테고리 번호: 100000200010025
            alt_url = "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000200010025"
            print(f"대안 URL 이동: {alt_url}")
            await page.goto(alt_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
        print("현재 URL:", page.url)
        print("현재 타이틀:", await page.title())
        
        # 상품 존재 여부 체크
        content = await page.content()
        print("HTML 길이:", len(content))
        
        # 상품 수집용 클래스가 있는지 검증
        prd_names = await page.locator("p.tx_name").all_inner_texts()
        print(f"발견된 tx_name 상품 수: {len(prd_names)}")
        for name in prd_names[:5]:
            print("-", name)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore())
