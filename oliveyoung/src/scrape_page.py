"""
올리브영 카테고리 페이지에서 플레이라이트(Playwright)를 사용해 상품 데이터를 수집하는 스크립트입니다.
세션 쿠키 및 접근 권한 우회를 위해 먼저 메인 페이지를 접속한 뒤 카테고리 페이지로 이동합니다.
"""

import asyncio
import os
import csv
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_page():
    main_url = "https://www.oliveyoung.co.kr/"
    target_url = "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000200010025&fltDispCatNo=&prdSort=01&pageIdx=1&rowsPerPage=24"
    
    async with async_playwright() as p:
        # 헤드리스 모드로 크로미움 브라우저 기동
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security"
            ]
        )
        
        # 일반 유저처럼 보이기 위한 컨텍스트 설정
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ko-KR",
            timezone_id="Asia/Seoul"
        )
        
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        
        # 1. 먼저 메인 페이지에 접속하여 세션 및 기본 쿠키 생성
        print(f"1. 올리브영 메인 페이지 접속 시도: {main_url}")
        await page.goto(main_url, wait_until="domcontentloaded")
        print("메인 페이지 로딩 완료. 쿠키 적재를 위해 3초 대기합니다...")
        await page.wait_for_timeout(3000)
        
        # 2. 메인 페이지 쿠키 상태에서 카테고리 페이지로 이동
        print(f"2. 올리브영 카테고리 페이지 이동 시도: {target_url}")
        await page.goto(target_url, wait_until="domcontentloaded")
        
        print("카테고리 페이지 로딩 대기 중 (5초)...")
        await page.wait_for_timeout(5000)
        
        title = await page.title()
        print(f"페이지 타이틀: {title}")
        
        content = await page.content()
        
        # 디버깅을 위한 HTML 소스 저장
        os.makedirs("oliveyoung/data", exist_ok=True)
        with open("oliveyoung/data/page_dump_real.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("HTML 덤프가 oliveyoung/data/page_dump_real.html에 저장되었습니다.")
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 상품 리스트 요소 파싱
        # 올리브영 카테고리관 상품 목록 CSS 선택자: 'ul.cate_prd_list li'
        products = soup.select("ul.cate_prd_list > li")
        print(f"파싱된 상품 수: {len(products)}")
        
        # 만약 ul.cate_prd_list li로 수집이 안될 경우 다른 선택자 시도
        if len(products) == 0:
            products = soup.select(".prd_info")
            print(f"대체 선택자(.prd_info) 파싱 상품 수: {len(products)}")
            
        collected_data = []
        
        for prd in products:
            # 브랜드명
            brand_elem = prd.select_one(".tx_brand")
            brand = brand_elem.get_text(strip=True) if brand_elem else ""
            
            # 상품명
            name_elem = prd.select_one(".tx_name")
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            # 만약 .prd_info 선택자를 쓴 경우 상위에서 찾거나 내부에서 검색
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
            print("수집된 상품 데이터가 없습니다. 선택자를 재점검하거나 HTML 덤프 파일을 확인해 주세요.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_page())
