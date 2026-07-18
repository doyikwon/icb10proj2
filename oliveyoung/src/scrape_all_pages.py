"""
올리브영 카테고리 페이지에서 페이지네이션(div.pageing)을 제어하여 
1페이지부터 마지막 페이지까지 순차적으로 900여 개 상품 데이터를 전부 수집하고 CSV로 저장하는 스크립트입니다.
"""

import asyncio
import os
import csv
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def go_to_page(page, page_num):
    """
    원하는 페이지 번호로 이동하는 안전한 페이징 클릭 함수입니다.
    """
    selector = f'div.pageing a[data-page-no="{page_num}"]'
    
    # 만약 타겟 페이지 번호가 화면에 직접 노출되어 있으면 클릭
    if await page.locator(selector).is_visible():
        print(f"[{page_num} 페이지] 클릭 시도...")
        await page.click(selector)
    else:
        # 노출되어 있지 않다면 '다음 10개' 페이지 그룹 버튼(a.next) 클릭
        next_selector = 'div.pageing a.next'
        if await page.locator(next_selector).is_visible():
            print(f"다음 페이지 그룹 이동을 위해 '다음' 버튼 클릭...")
            await page.click(next_selector)
            await page.wait_for_timeout(2000)
            # 재귀적으로 다시 타겟 페이지 클릭 시도
            await go_to_page(page, page_num)
        else:
            raise Exception(f"{page_num} 페이지 링크를 찾을 수 없으며, 다음 그룹 이동도 불가능합니다.")

async def scrape_all_pages():
    main_url = "https://www.oliveyoung.co.kr/"
    collected_data = []
    
    async with async_playwright() as p:
        print("구글 크롬 브라우저 채널(channel='chrome')을 헤드풀 모드로 기동합니다...")
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
        
        # 1. 메인 페이지 방문
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
        
        await page.evaluate(js_code)
        
        print("상품 목록 요소(ul.cate_prd_list)가 나타날 때까지 대기합니다. (최대 60초)")
        print("※ 보안 체크 체크박스 화면이 나타나면 직접 클릭해 주세요.")
        
        # 1페이지 로드 확인
        await page.wait_for_selector("ul.cate_prd_list", timeout=60000)
        print("1페이지 로드 완료!")
        await page.wait_for_timeout(2000)
        
        # 전체 페이지 수 계산
        content_init = await page.content()
        soup_init = BeautifulSoup(content_init, 'html.parser')
        
        total_count_elem = soup_init.select_one(".cate_info_tx span, .total_count, #totCnt")
        total_count = 947 # 기본값
        if total_count_elem:
            try:
                raw_text = total_count_elem.get_text(strip=True).replace(",", "")
                total_count = int(raw_text)
                print(f"감지된 전체 상품 수: {total_count}개")
            except Exception as e:
                print("상품 수 파싱 실패, 기본 947개로 진행:", e)
                
        # 1페이지당 24개 상품 기준 전체 페이지 계산
        total_pages = (total_count + 23) // 24
        print(f"총 수집 목표 페이지 수: {total_pages} 페이지")
        
        # 페이지 루프 실행
        for current_page in range(1, total_pages + 1):
            print(f"\n================ [ {current_page} / {total_pages} 페이지 수집 진행 ] ================")
            
            # 1페이지가 아니면 해당 페이지로 이동
            if current_page > 1:
                try:
                    await go_to_page(page, current_page)
                    # 활성화된 페이지 번호가 현재 페이지 번호와 일치할 때까지 대기
                    await page.wait_for_selector(f'div.pageing strong:has-text("{current_page}")', timeout=10000)
                    print(f"{current_page} 페이지 전환 확인 완료.")
                    await page.wait_for_timeout(2500) # 상품 로딩 안전 대기
                except Exception as e:
                    print(f"{current_page} 페이지 이동 실패, 수집을 스킵합니다. 오류:", e)
                    continue
            
            # 스크롤 다운을 수행하여 지연 로딩 이미지 및 정보 갱신
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2);")
            await page.wait_for_timeout(1000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await page.wait_for_timeout(1500)
            
            # HTML 파싱
            page_content = await page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            products = soup.select("ul.cate_prd_list > li")
            
            if len(products) == 0:
                products = soup.select(".prd_info")
                
            print(f"이 페이지에서 추출된 상품 수: {len(products)}")
            
            page_items_count = 0
            for prd in products:
                brand_elem = prd.select_one(".tx_brand")
                brand = brand_elem.get_text(strip=True) if brand_elem else ""
                
                name_elem = prd.select_one(".tx_name")
                name = name_elem.get_text(strip=True) if name_elem else ""
                
                if not name:
                    name_elem = prd.select_one(".prd_name")
                    name = name_elem.get_text(strip=True) if name_elem else ""
                
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
                    page_items_count += 1
            
            print(f"{current_page} 페이지에서 {page_items_count}개 상품 성공적으로 추출 완료.")
            
        # CSV 파일 전체 저장
        csv_file_path = "oliveyoung/data/oliveyoung_products.csv"
        if collected_data:
            with open(csv_file_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["brand", "name", "original_price", "discount_price", "url"])
                writer.writeheader()
                writer.writerows(collected_data)
            print(f"\n[수집 완료] 총 {len(collected_data)}개의 상품 정보를 수집하여 {csv_file_path}에 저장했습니다.")
        else:
            print("수집된 상품 데이터가 전혀 없습니다.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_all_pages())
