"""
실제 설치된 구글 크롬 브라우저 채널(channel="chrome")을 사용하여
Cloudflare 인증 및 보안 챌린지가 발생할 경우 최대 60초 대기하며 수집을 지속하는 스크립트입니다.
"""

import asyncio
import os
import csv
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_page():
    main_url = "https://www.oliveyoung.co.kr/"
    
    async with async_playwright() as p:
        print("구글 크롬 브라우저 채널(channel='chrome')을 헤드풀 모드로 구동합니다...")
        browser = await p.chromium.launch(
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="ko-KR",
            timezone_id="Asia/Seoul"
        )
        
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()
        
        # 1. 메인 페이지 로드
        print(f"1. 메인 페이지 접속: {main_url}")
        await page.goto(main_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # 2. 내장 카테고리 이동 함수 실행
        print("2. 자바스크립트 전이 함수 실행을 통한 영양제관 이동...")
        js_code = """
        common.link.moveCategory('100000200010025', 'Cat100000200010025_MID', 'Drawer', {
            t_page: '대메뉴_카테고리', 
            t_click: '카테고리_중카테고리', 
            t_1st_category_type: '대_건강식품', 
            t_2nd_category_type: '중_영양제'
        });
        """
        
        # 단순 클릭/함수실행 요청을 보낸 뒤, 리다이렉션으로 인해 컨텍스트가 임시 해제될 수 있으므로
        # 상품 리스트 선택자가 보일 때까지 여유롭게 대기합니다.
        try:
            await page.evaluate(js_code)
            print("이동 함수 호출 완료.")
        except Exception as e:
            print("이동 함수 호출 중 예외 발생 (리다이렉션으로 인한 가능성):", e)
            
        print("상품 목록 요소(ul.cate_prd_list)가 나타날 때까지 대기합니다. (최대 60초)")
        print("※ 화면에 '사람인지 확인하십시오' 체크박스가 나타나면 클릭해 주세요.")
        
        try:
            # 60초 대기
            await page.wait_for_selector("ul.cate_prd_list", timeout=60000)
            print("상품 목록 로딩이 감지되었습니다!")
        except Exception as e:
            print("오류: 상품 목록 요소를 로드하지 못했습니다. (타임아웃)", e)
            
        print("페이지 안정화 대기 및 스크롤 다운을 수행합니다...")
        await page.wait_for_timeout(3000)
        
        # 안전한 스크롤 다운
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2);")
            await page.wait_for_timeout(1500)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await page.wait_for_timeout(2000)
        except Exception as e:
            print("스크롤 제어 중 오류 발생:", e)
            
        content = await page.content()
        
        # 디버그용 HTML 덤프 저장
        os.makedirs("oliveyoung/data", exist_ok=True)
        with open("oliveyoung/data/page_dump_real.html", "w", encoding="utf-8") as f:
            f.write(content)
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # 상품 리스트 파싱
        products = soup.select("ul.cate_prd_list > li")
        print(f"파싱된 상품 수 (ul.cate_prd_list > li): {len(products)}")
        
        if len(products) == 0:
            products = soup.select(".prd_info")
            print(f"대체 선택자(.prd_info) 파싱 상품 수: {len(products)}")
            
        collected_data = []
        
        for prd in products:
            # 브랜드명 (.tx_brand)
            brand_elem = prd.select_one(".tx_brand")
            brand = brand_elem.get_text(strip=True) if brand_elem else ""
            
            # 상품명 (.tx_name)
            name_elem = prd.select_one(".tx_name")
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            if not name:
                name_elem = prd.select_one(".prd_name")
                name = name_elem.get_text(strip=True) if name_elem else ""
            
            # 가격 정보
            price_elem = prd.select_one(".prd_price")
            original_price = ""
            discount_price = ""
            
            if price_elem:
                org_elem = price_elem.select_one(".tx_org")
                if org_elem:
                    original_price = org_elem.get_text(strip=True).replace("원", "").replace(",", "")
                
                cur_elem = price_elem.select_one(".tx_cur")
                if cur_elem:
                    discount_price = cur_elem.get_text(strip=True).replace("원", "").replace(",", "")
                    
                if not original_price and discount_price:
                    original_price = discount_price
                    
            # 링크
            link_elem = prd.select_one("a")
            link = ""
            if link_elem and link_elem.has_attr("href"):
                link = link_elem["href"]
                if not link.startswith("http"):
                    link = "https://www.oliveyoung.co.kr" + link
            
            if name:
                collected_data.append({
                    "brand": brand,
                    "name": name,
                    "original_price": original_price,
                    "discount_price": discount_price,
                    "url": link
                })
        
        # CSV 파일 저장
        csv_file_path = "oliveyoung/data/oliveyoung_page1.csv"
        if collected_data:
            with open(csv_file_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["brand", "name", "original_price", "discount_price", "url"])
                writer.writeheader()
                writer.writerows(collected_data)
            print(f"성공적으로 {len(collected_data)}개의 상품 정보를 수집하여 {csv_file_path}에 저장했습니다.")
            print("\n[수집된 데이터 샘플 (상위 5개)]")
            for idx, item in enumerate(collected_data[:5]):
                print(f"{idx+1}. [{item['brand']}] {item['name']} | 정가: {item['original_price']}원 | 할인가: {item['discount_price']}원")
        else:
            print("수집된 상품 데이터가 없습니다. HTML 구조나 덤프를 재확인하세요.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_page())
