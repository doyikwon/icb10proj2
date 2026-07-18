"""
올리브영 카테고리 페이지 로딩 시 발생하는 모든 네트워크 요청(AJAX 및 API 호출)을 캡처하여
실제 상품 데이터를 가져오는 API endpoint 주소를 탐색하는 진단 스크립트입니다.
"""

import asyncio
from playwright.async_api import async_playwright

async def run():
    target_url = "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000200010025"
    
    async with async_playwright() as p:
        print("헤드풀 모드로 브라우저 기동 및 네트워크 감시 시작...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()
        
        # 네트워크 요청 및 응답 이벤트 리스너 등록
        api_requests = []
        
        async def handle_request(request):
            url = request.url
            # 정적 파일(.js, .css, .png 등)은 제외하고 관심 대상 URL만 기록
            if any(ext in url for ext in [".do", "ajax", "json", "API", "list", "goods"]):
                if not any(exclude in url for exclude in [".js", ".css", ".png", ".jpg", ".gif", "datadog", "facebook"]):
                    api_requests.append((request.method, url))
        
        async def handle_response(response):
            url = response.url
            if any(ext in url for ext in [".do", "ajax", "json"]):
                if not any(exclude in url for exclude in [".js", ".css", ".png", ".jpg", ".gif", "datadog", "facebook"]):
                    try:
                        content_type = response.headers.get("content-type", "")
                        # JSON 형태의 응답인 경우 첫 일부를 출력
                        if "json" in content_type:
                            text = await response.text()
                            print(f"\n[Response JSON] {url[:100]}...\nContent snippet: {text[:200]}\n")
                    except Exception:
                        pass

        page.on("request", handle_request)
        page.on("response", handle_response)
        
        print(f"올리브영 메인 홈 접속 및 세션 활성화...")
        await page.goto("https://www.oliveyoung.co.kr/", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        print(f"카테고리 이동 시도: {target_url}")
        # 자바스크립트를 이용해 안전하게 이동
        js_code = "common.link.moveCategory('100000200010025', 'Cat100000200010025_MID', 'Drawer');"
        await asyncio.gather(
            page.wait_for_load_state("domcontentloaded"),
            page.evaluate(js_code)
        )
        
        print("페이지 로딩 대기 (10초)...")
        await page.wait_for_timeout(10000)
        
        print("\n=== 감지된 API 및 AJAX 요청 목록 ===")
        for method, url in set(api_requests):
            print(f"- [{method}] {url}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
