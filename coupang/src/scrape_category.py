"""
Coupang 카테고리 스크래핑 스크립트

목적: scrapling 라이브러리를 사용하여 쿠팡 카테고리 페이지의 상품명, 가격, 평점 및 리뷰 수를 수집합니다.
기능:
1. 첫 번째 페이지 수집 테스트 후 정상 작동 시 CSV 저장
2. 전체 페이지 순회하며 SQLite 데이터베이스에 수집한 정보 저장
작성자: Antigravity
생성일: 2026-06-22
"""

import os
import time
import sqlite3
import pandas as pd
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import re
import json

# 기본 정보 설정
# 팁: _rsc 파라미터는 Next.js RSC 페이로드를 반환하므로 HTML 파싱을 위해 기본 URL을 사용합니다. 
# 만약 차단된다면 헤더와 파라미터를 그대로 사용해야 할 수 있습니다.
BASE_URL = "https://www.coupang.com/np/categories/305798"

HEADERS = {
    "cookie": "PCID=17783699071059948981675; MARKETID=17783699071059948981675; x-coupang-target-market=KR; x-coupang-accept-language=ko-KR; sid=efc0d5eb3b2249f68435b057b16d19ce69dcc91c; trac_src=1042016; trac_spec=10304903; trac_addtag=900; trac_ctag=HOME; trac_lptag=%EC%BF%A0%ED%8C%A1; trac_itime=20260627133837; bm_ss=ab8e18ef4e; bm_so=3357518B916B5B3B004FC03D50AA03F7FECF45E64C85E115B2143858E3F425E3~YAAQ5Ij+eek3nvyeAQAAhF1fBwgMQwgOtWsfU5+zS6X5vG4sm843d4aJ0tsKVuMTAf6SYzTQ4E+7EGqaOhTb9AsrV4Gr9ueMrTBoNwk33cV0gtmuJ8WUufdNWMGh4UkIpzSA/FuP3rxvwoAMqFZRopZoH9ujDfJlFGLOWu/OINeggUpGvskGemqF+ScnfF0llxImx2280/CCoo+PO3UGL8cyhtaYQ+PwN6hPzbKNNV7VT/eR+PcwVisnvKfnxGT3vlJ2u3cZqnYJWOxgOiTaNIczdITAK1h4W3wxHEf5d2MG2Qrz5HbhhRCMsaaGpc02RTuqLtKy0J035+evO7avpdfWaJqG8J1Fw+weLjzV2KDVG7ByfzfQSA36jOEDDQLU2COzXRPm9Bzi+09ptNVyfRAGNIm8GYYyDQi7sU18wCGDndTYA4BbsJOdpsxdHq1MHCXSnIzx9X7SuNz0CbxUki8XF1qA; bm_mi=1AFD132A0194E0CB836DC34BDD3A4F1D~YAAQ5Ij+edA4nvyeAQAAdWZfBwCjiZ1U+jgIoRgE3Z8nSe3xqUuyIPthIpyDdI+PwczzbAsLm/bTmFKJsTbSi2wwzMlO8XfhnOnGL4xnnOJAhm72Ci6eOrh8eql32cdZlGdps4nVTdz3qVbyZ+2GE3Tpz1kaT/0XeMDW8PaiCRlCGuTNhbPorzryHHvazSfFJytkp/YpERQc2aUDxTm3OqFyEADl75DKW61vEQKQ04c0JkBDHhmADP2/Rwd98hXyx5KgdKqqR9XnlHHNZNP2hNl9GGERXnB1CMvxdkngONWcBkyReerZLCPoRmjK7TaHRqwk8Ga/169ebV9oc6W+1hy3nM9d~1; bm_lso=3357518B916B5B3B004FC03D50AA03F7FECF45E64C85E115B2143858E3F425E3~YAAQ5Ij+eek3nvyeAQAAhF1fBwgMQwgOtWsfU5+zS6X5vG4sm843d4aJ0tsKVuMTAf6SYzTQ4E+7EGqaOhTb9AsrV4Gr9ueMrTBoNwk33cV0gtmuJ8WUufdNWMGh4UkIpzSA/FuP3rxvwoAMqFZRopZoH9ujDfJlFGLOWu/OINeggUpGvskGemqF+ScnfF0llxImx2280/CCoo+PO3UGL8cyhtaYQ+PwN6hPzbKNNV7VT/eR+PcwVisnvKfnxGT3vlJ2u3cZqnYJWOxgOiTaNIczdITAK1h4W3wxHEf5d2MG2Qrz5HbhhRCMsaaGpc02RTuqLtKy0J035+evO7avpdfWaJqG8J1Fw+weLjzV2KDVG7ByfzfQSA36jOEDDQLU2COzXRPm9Bzi+09ptNVyfRAGNIm8GYYyDQi7sU18wCGDndTYA4BbsJOdpsxdHq1MHCXSnIzx9X7SuNz0CbxUki8XF1qA~1782535119569; bm_sz=3327338B26479C5B7ECEB5D6AAF0B4CC~YAAQ5Ij+eRc8nvyeAQAAhYJfBwAc7022aQrYqbdGAZlARNiRN1YtT+u7+1DqW8kt7s+MjPFoZsFPeaiQHhPsZxduuS1ZpvyiAwkcFj2sGjIdaHjamnlrmgcpn0r2h4txoccYwePu5EA/mU6FZRwZqvv5saeWLJpIXScbnmp3CGhH14Aa8/BSA0O3P3cqbYh+Dyp/UPmU0QBw015RaDBHeM3f0Fr0jJeE2JceF7BH9ujrbZFCAx0tOJyDp6e0CcRpkqG1iu/vpngz29udVvV6lrMlDzJPjRqrvV71zYy7enPA/1WdQKbCE821NG3VTYwDEEkfufJTfkJDNtKbOJ4UiRA1cZ63X/+V2BTRsYdEdxq/ytNXki+3IpcbNm50QehjSR2ZKzx+NdX4Mfux8R2Rfqn5Rna+2nlniOX26A==~4534596~3293489; x-cp-s=YzE9MyZjMj0xLjAuMCZjMz0xNzgyNTM1MTI2NzMxJmM0PVNIUm9LMmhKY1VWNGJVSXdjMHBxZDJsd1JESm9SVk5CT1Vsd1IyMU1OMjlZY2xOaGFVeEVXVGhJUzBsdWFqUm5TME54SzJ0TmNXZHJjMHh2Ym5WSksydHlZbFYxUVZOUFRtOWlNakZ5WWxjd1RUZHRORUZ2WXpSSVNYVmFhalJKVkVKVU1sVkVkeXRGYzFKdk1HNUJkMUZFWjJ0VGFsRTBWMGhKZFVKR1dqWmlUV2M5JmM1PWNvbS5jb3VwYW5nLndlYiZjNj0mYzc9JmM4PTk1MGE3NTVkOTNkMzRkMWI4YjYzMzM4N2IwNDU1NWU0JmM5PTEmczE9dTMxaGFTZWxkWjh1K0J6QWk0S0tnM0kxSlJqeTJHQ2hxTzI3dGdFdS9Zdz0mczI9MS4wLjA=; _abck=2E0430660BD46EF924CB45ED75DE9830~0~YAAQ5Ij+eSA8nvyeAQAA6YJfBxAgkRU3F4dOUvHXKpTF7EJLmNhzxGCCYYSaAVs8d0vzRtdqNyxg/ritg4+daniQFE7mnj53lqMrJdR5FmNhQ+Z4tL3NehvmjyH3JECSQmu+scFM/nCQcv+XE0w0FL1FBa0dVeLRRkQuCWHTBBnUk5iHZaCrn5ZB0J+Yj3NAY7QQBBeSi3UJajf3bonxnhKyQYAzcHks1GBa1bYIkxia9czCDX3CGw4JrWmK3wgcd3AMl4qckR0k8kHykMctnG/fQzZuahJVVzzjW2P/tx3mWVLSwxkrND8IqMWanNg3vWOeo5xySghLHdu1IREMt/i38rfnL/hys2+NMYmzJwVpuhYY+IJQtLu1+pyzapg5gmqQnvobbfg3aYL+jSNVckvluPLRSbUsvOEFOp3pcJqAJ6NIpcUzrQCU/nzkDQymF4uKK6h6Hcenw+AFp4cExzBNU2IPHCJZpZM9N1TQp/VsZPm15Ygpa/0MDB/TyeEBbvdKnQe89YLrQ/RryVkBxqvLlVdW4XHCcGQYqpGV6QPpOXtOPUR+OR9066//ooiZKEFT/CQRSvVM6F/CeWXnO0VakeakaDTMPpgfIQwAcvDA+7xUB2buyedLIYh5Bdm8vpYWTN+zykIg/JsqyKDQk9E=~-1~-1~1782538718~AAQAAAAF%2f%2f%2f%2f%2f1DnQhNV+3Hq3zXl2P44Mjqk%2fFHCHtXnKnbune6K4Lyn92WS%2fPbxuptVeGytVTXAvimOffFUjux1RHmAZ%2f4yNEwYm2AYbgjPoUVl~-1; ak_bmsc=6962E486D0D1602D285CFCF2C25C54F7~000000000000000000000000000000~YAAQ5Ij+eWQ8nvyeAQAAWoZfBwC1qNTS7coUSJrOz3hVtlchuf4/YoKPcQJqlpAsKzxZ+Cv3rfbQ4H8jouQbXH44h4ohFlFrxqVm//YvjCl+5f56fIO3KVTry6ebcFzYlqnWTGcw44OxmKSfTqHgspWt9TWEr7Gz5IALCh8phsT04iDlxvXlW2uGwUDsN6EwMDnkuX76JXjKdn25Jm9yOyX4bj9vcxJnkvREtRRaFUZz5Nbit2p0rp7JU3Jx8Nv+f/eeTdvRa4JGLGkPkBHHYY1ilOvbn44ssqEhr+mDgN/x13yB1PmdIBIwP8GP1AfX/qW8sGfpKy0tXJHdtxy6gOsJCry/WV7BOH+A35jFDBbUYmKX+nM8GuWSfMq6xmE6d1ldTxtyfpBzWquWko0OCdyXNJYBjFBST6aBuoiW3g12TLZUOAQpWtVsSfvfHVi1C4Ft7QDf9SMKGMNGxM2OFz8Zyv2D/hOesCWOci/HjnegvasqxX3ABt0DWoFc5s2H+EUQfjdeeVV7Hg==; bm_sv=43C9FB71E37E2414F6C9D088ACD6120B~YAAQ5Ij+eRA9nvyeAQAAqI5fBwDUDoa+97c+86B2jBE3aCdXP09yPhVP99p2nENytKCEvlj4Ngx/JOphwmq8JIjFGMSq4Hgj0KsDUQHtYVAh6aIpEVuV/8vM35tG6Ci5hlGJOHNWCo8XDBFM8OsTh9rNJ6x6KFLorMr0O5l7dW5gHv8tR6SOeEI1Vre4kZvh8hUVB6tnhjLSUjUp7ev4dGE6nYhuatHaKYs25vQeWQ6IJ9wR6wscN0X86TdSp0YNVg==~1; bm_s=YAAQ5Ij+eZFDnvyeAQAAaM5fBwXdBjee94kSgh0hdJ8kj00AN8qzoprICh2iNtVFLJTigNWGhsRz69VeQI7jtVPU3nUvBRmhPvP9gyDxt1cpQHi0BkKXLkSClGa8zHsYlVecG7BzNxBhOfhQNwySlH4GJsjvqA6LAfl1naHiq08msqanZJY35ieMhK7OjAlXQ4tdqEU7BdCx2xsghMA9M1P+vqMRm1x9WI+lqzD6zPfMwBSOkSMDFdflQotiZLpFA1DWZWXHquhTZ792TPkSPe8mJTrrhRgmh+H9860P6OqUnZd7sZ07404tRa9sIAvp3K2WyknnnaxxkdRRxIVeo/+bCc4drcMdwoTKDm9BJxVyXnTSdiKS4DYMvq96TPIecAszH1RtWkzkFghWdxXYK6z+teq7jLPAU2fI9G7lnyc4FxTfZWCqJWy8C0ri0iiNtQ9jBkjwkcg6d3+etDTZPmzkJfRH2v8NcFVvoKMV9Kv/X+fkVzQGl2fPbY1354sPvDUVijq0ijhfmn9uCZlvyoeOBEYakK5mXgVjUG07nyEluwmWI9NSnxt+XfiTHc37v92Z2PeJ5sGV/jxYlW4EJXoF8IhkMtUiH8xO40Sahxa8rTc4KkL8WqdCqCDt3/FDUVZZ/ytgG7QHvaRtX6q07+OO/Uq0A9IsuKFJUme/f3B5Hqe7Pa3FVSsHKvon1tTYnphnhQnbgPBghHg5s8TpQ6kJDsZK5JW4ywRRrSQJgsytHR2qhodY4wJxtljfYyE2bwcJiOx+08rPSbkvd04SYdjmpUixSTnmANbm6zdfMT63Oi/K8gycDhbi2VfptdnZiRQxxCl5Nw0rooFF0LNnp5HfqgXkAtifSrxJN1OgJ6/bxFsIARh+TKzB39YVw/QuK69E71Di56GenqfS9AaYw5A6//rgNkfYwuyDx/Cyrw7TLtyZsDHmpdYGCfHt+nS4ZDUMp1rI59Vd4lQ7GXOnPXZwyRVaJcnjUpodBf5PYoLO",
    "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "priority": "u=0, i",
    "referer": "https://www.coupang.com/?src=1042016&spec=10304903&addtag=900&ctag=HOME&lptag=%EC%BF%A0%ED%8C%A1"
}

def extract_products_from_html(html_text):
    """
    HTML에서 상품 데이터를 추출합니다. 
    1차로 JSON-LD를 시도하고, 없으면 Next.js DOM 구조 기반으로 추출합니다.
    """
    soup = BeautifulSoup(html_text, 'html.parser')
    products = []
    
    # 1. application/ld+json 시도 (주로 첫 페이지에만 존재)
    script_tags = soup.find_all('script', type='application/ld+json')
    for tag in script_tags:
        try:
            if not tag.string: continue
            data = json.loads(tag.string)
            data_list = [data] if isinstance(data, dict) else data
            for d in data_list:
                if d.get('@type') == 'ItemList' and 'itemListElement' in d:
                    for element in d['itemListElement']:
                        item = element.get('item', {})
                        if item.get('@type') == 'Product':
                            name = item.get('name', '이름 없음')
                            offers = item.get('offers', {})
                            price = int(offers.get('price', 0)) if offers else 0
                            rating_info = item.get('aggregateRating', {})
                            rating = float(rating_info.get('ratingValue', 0.0)) if rating_info else 0.0
                            review_count = int(rating_info.get('reviewCount', 0)) if rating_info else 0
                            url = item.get('url', '')
                            products.append({"name": name, "price": price, "rating": rating, "review_count": review_count, "deep_link": url})
        except Exception:
            continue
            
    if products:
        return products
        
    # 2. DOM 파싱 시도 (페이지 2번 이상에서 JSON-LD 누락 시)
    product_links = soup.find_all('a', href=lambda x: x and '/vp/products/' in x)
    seen_urls = set()
    
    for a_tag in product_links:
        try:
            url = a_tag.get('href', '')
            if url and url.startswith('/'):
                url = "https://www.coupang.com" + url
            
            text = a_tag.get_text(separator='|', strip=True)
            if not text:
                continue
                
            texts = [t.strip() for t in text.split('|') if t.strip()]
            
            name = "이름 없음"
            for t in texts:
                if len(t) > 3 and '원' not in t and '적립' not in t and '%' not in t:
                    name = t
                    break
            
            if name == "이름 없음" and texts:
                 name = texts[0]
                 
            price = 0
            for t in reversed(texts):
                if '원' in t and not any(skip in t for skip in ['(', ')', '정', '개', '최대', '적립', '당', 'ml', 'g']):
                    num_str = re.sub(r'[^0-9]', '', t)
                    if num_str:
                        price = int(num_str)
                        break
                        
            rating = 0.0
            review_count = 0
            for t in texts:
                match = re.search(r'([0-5]\.[0-9])\s*\((.*?)\)', t)
                if match:
                    rating = float(match.group(1))
                    review_count = int(re.sub(r'[^0-9]', '', match.group(2)))
                    break
                    
            if price > 0 and url not in seen_urls:
                products.append({
                    "name": name,
                    "price": price,
                    "rating": rating,
                    "review_count": review_count,
                    "deep_link": url
                })
                seen_urls.add(url)
        except Exception:
            continue
            
    return products

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS products')
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            rating REAL,
            review_count INTEGER,
            deep_link TEXT
        )
    ''')
    conn.commit()
    return conn

def save_to_db(conn, products):
    cursor = conn.cursor()
    for p in products:
        cursor.execute('''
            INSERT INTO products (name, price, rating, review_count, deep_link)
            VALUES (?, ?, ?, ?, ?)
        ''', (p["name"], p["price"], float(p["rating"]), int(p["review_count"]), p.get("deep_link", "")))
    conn.commit()

def main():
    # 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    csv_path = os.path.join(data_dir, "coupang_first_page.csv")
    db_path = os.path.join(data_dir, "coupang_products.db")

    print("=== 브라우저 구동 및 스크래핑 시작 ===")
    
    with sync_playwright() as p:
        # headless=False로 실제 브라우저 화면을 띄워서 우회합니다.
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=HEADERS.get("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36")
        )
        Stealth().apply_stealth_sync(context)
        
        # 쿠키 적용
        if "cookie" in HEADERS:
            cookies_list = []
            for cookie in HEADERS["cookie"].split(";"):
                if "=" in cookie:
                    name, value = cookie.strip().split("=", 1)
                    cookies_list.append({
                        "name": name,
                        "value": value,
                        "domain": ".coupang.com",
                        "path": "/"
                    })
            context.add_cookies(cookies_list)
            
        page_browser = context.new_page()

        print("=== 1단계: 첫 페이지 수집 테스트 ===")
        page_num = 1
        
        url = f"{BASE_URL}?traceId=mqp7ucta&page={page_num}"
        page_browser.goto(url, wait_until="domcontentloaded")
        
        # 캡차를 수동으로 풀거나 렌더링될 때까지 최대 30초 대기
        products = []
        for _ in range(15):
            page_browser.wait_for_timeout(2000)
            html_content = page_browser.content()
            products = extract_products_from_html(html_content)
            if products:
                break
        
        if not products:
            print("오류: 상품 데이터를 찾을 수 없습니다. 쿠팡 구조가 변경되었거나 차단(캡차)일 수 있습니다.")
            return
            
        print(f"첫 페이지에서 {len(products)}개의 상품을 성공적으로 수집했습니다.")
        
        # CSV 저장
        df = pd.DataFrame(products)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"첫 페이지 수집 결과 CSV 저장 완료: {csv_path}")
        
        print("\n=== 2단계: 전체 상품 수집 및 SQLite 저장 ===")
        conn = init_db(db_path)
        save_to_db(conn, products) # 첫 페이지 데이터 저장
        
        page_num = 2
        
        while page_num <= 10:
            page_browser.wait_for_timeout(3000) # 서버 부하 및 차단 방지용 딜레이
            print(f"페이지 {page_num} 수집 중...")
            
            url = f"{BASE_URL}?traceId=mqp7ucta&page={page_num}"
            page_browser.goto(url, wait_until="domcontentloaded")
            
            page_products = []
            for _ in range(15):
                page_browser.wait_for_timeout(2000)
                html_content = page_browser.content()
                page_products = extract_products_from_html(html_content)
                if page_products:
                    break
            
            if not page_products:
                print(f"페이지 {page_num}에 더 이상 상품이 없습니다. 수집을 종료합니다.")
                break
                
            save_to_db(conn, page_products)
            print(f"페이지 {page_num}에서 {len(page_products)}개 상품 수집 및 DB 저장 완료.")
            
            page_num += 1

        browser.close()
        conn.close()
        print(f"\n모든 수집이 완료되었습니다. 데이터는 {db_path} 에 저장되었습니다.")

if __name__ == "__main__":
    main()
