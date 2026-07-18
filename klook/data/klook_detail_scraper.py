"""
Klook 상품 상세 페이지 크롤링 스크립트.

기능:
- klook_products.db의 products 테이블에서 상위 10개 상품의 URL을 추출합니다.
- Playwright를 사용하여 실제 브라우저 환경에서 페이지에 접근합니다.
- 상세 페이지의 제목, 주요 설명, 이미지 URL 등을 수집합니다.
- 수집된 데이터를 product_details 테이블에 저장합니다.
"""

import sqlite3
import json
import time
import re
from playwright.sync_api import sync_playwright

DB_PATH = 'klook_products.db'

def setup_database():
    """데이터베이스에 product_details 테이블을 생성합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS product_details (
            product_id TEXT PRIMARY KEY,
            url TEXT,
            page_title TEXT,
            main_description TEXT,
            images_json TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')
    conn.commit()
    return conn

def get_top_products(conn, limit=150):
    """상위 상품의 ID와 URL을 가져옵니다. 이미 수집된 상품은 제외합니다."""
    c = conn.cursor()
    c.execute("SELECT product_id, deep_link FROM products WHERE deep_link IS NOT NULL LIMIT ?", (limit,))
    all_products = c.fetchall()
    
    # 이미 수집된 상품 확인
    c.execute("SELECT product_id FROM product_details")
    scraped_ids = {row[0] for row in c.fetchall()}
    
    # 수집되지 않은 상품만 필터링
    return [p for p in all_products if p[0] not in scraped_ids]

def scrape_product_details(page, url):
    """Playwright 페이지 객체를 통해 단일 상품 상세 정보를 스크래핑합니다."""
    print(f"Scraping URL: {url}")
    try:
        # 봇 탐지 우회를 위해 타임아웃과 wait_until 옵션을 적절히 조절
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # 페이지가 랜더링 될 시간을 줍니다
        page.wait_for_timeout(3000)
        
        page_title = page.title()
        
        # 설명 텍스트 수집: p 태그, h2 태그 위주로 추출하여 연결
        # Klook의 구조상 div 등의 텍스트도 많지만 너무 지저분해질 수 있으므로 본문 텍스트 전체를 가져옵니다.
        # body 하위의 보이는 텍스트를 적당히 잘라오거나, 의미있는 p 태그 추출
        texts = page.locator('p, h1, h2, h3').all_inner_texts()
        # 공백 제거 및 필터링
        filtered_texts = [text.strip() for text in texts if text.strip() and len(text.strip()) > 5]
        # 중복 제거 및 너무 긴 텍스트 합치기 (최대 3000자 제한)
        main_description = "\n".join(filtered_texts)
        if len(main_description) > 5000:
            main_description = main_description[:5000] + "..."
            
        # 이미지 URL 수집
        images = page.locator('img').element_handles()
        image_urls = []
        for img in images:
            src = img.get_attribute('src')
            if src and src.startswith('http'):
                image_urls.append(src)
                
        # 대표 이미지를 위해 앞쪽 10개만 저장 (너무 많으면 DB 용량 차지)
        images_json = json.dumps(list(set(image_urls))[:10])
        
        return {
            'page_title': page_title,
            'main_description': main_description,
            'images_json': images_json
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    conn = setup_database()
    products = get_top_products(conn, limit=150)
    
    if not products:
        print("상품 데이터가 없습니다.")
        return

    print(f"총 {len(products)}개의 상품 정보를 수집합니다.")
    
    with sync_playwright() as p:
        # headless=False로 설정하여 봇 방지 우회
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        for product_id, url in products:
            if not url or not url.startswith('http'):
                print(f"잘못된 URL 건너뜀: {url}")
                continue
                
            details = scrape_product_details(page, url)
            
            if details:
                # DB 저장 (존재하면 업데이트)
                c = conn.cursor()
                c.execute('''
                    INSERT OR REPLACE INTO product_details 
                    (product_id, url, page_title, main_description, images_json, scraped_at) 
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    product_id, 
                    url, 
                    details['page_title'], 
                    details['main_description'], 
                    details['images_json']
                ))
                conn.commit()
                print(f"[{product_id}] 데이터 저장 완료.")
            else:
                print(f"[{product_id}] 수집 실패.")
                
            # 서버 과부하 방지 및 봇 탐지 우회를 위한 대기
            time.sleep(2)
            
        browser.close()
    
    conn.close()
    print("스크래핑 및 데이터베이스 저장 완료.")

if __name__ == "__main__":
    main()
