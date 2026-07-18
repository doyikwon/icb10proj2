"""
아이허브 스포츠 스페셜 특가 상품 데이터를 수집하여 SQLite 데이터베이스 및 CSV 파일로 저장하는 스크립트입니다.
페이지마다 데이터를 API에서 수집할 때마다 SQLite 데이터베이스(`iherb/data/sports_specials.db`)에 즉시 저장하며,
수집이 완료되면 전체 데이터를 `iherb/data/sports_specials_all.csv`로 저장합니다.
임시 서버 오류(예: 500 에러)에 대응할 수 있도록 페이지 요청 시 최대 3회의 재시도 메커니즘이 포함되어 있습니다.
"""

import sys
import json
import time
import sqlite3
import urllib.request
import urllib.parse
import pandas as pd

# Windows 콘솔 출력 인코딩 오류 방지
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = "iherb/data/sports_specials.db"
CSV_PATH = "iherb/data/sports_specials_all.csv"

def init_db():
    """SQLite 데이터베이스 및 테이블 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            productId INTEGER PRIMARY KEY,
            displayName TEXT,
            brandName TEXT,
            listPrice TEXT,
            discountPrice TEXT,
            rating REAL,
            ratingCount INTEGER,
            isOutOfStock INTEGER,
            url TEXT
        )
    """)
    conn.commit()
    return conn

def insert_products_to_db(conn, products):
    """수집된 상품 데이터를 SQLite DB에 삽입 (존재하는 경우 대체)"""
    cursor = conn.cursor()
    data_to_insert = []
    for p in products:
        data_to_insert.append((
            p.get("productId"),
            p.get("displayName"),
            p.get("brandName"),
            p.get("listPrice"),
            p.get("discountPrice"),
            p.get("rating"),
            p.get("ratingCount"),
            1 if p.get("isOutOfStock") else 0,
            p.get("url")
        ))
    
    cursor.executemany("""
        INSERT OR REPLACE INTO products (
            productId, displayName, brandName, listPrice, discountPrice, rating, ratingCount, isOutOfStock, url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data_to_insert)
    conn.commit()

def fetch_page_with_retry(full_url, headers, max_retries=3, delay=2):
    """오류 발생 시 재시도 메커니즘을 포함하여 페이지 요청 수행"""
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            if attempt == max_retries:
                raise e
            print(f" [오류 발생: {e} - {attempt}회차 재시도 중...]", end="", flush=True)
            time.sleep(delay)

def main():
    base_url = "https://catalog.app.iherb.com/category/sports/specials"
    page = 1
    page_size = 18
    all_products = []

    # DB 초기화
    conn = init_db()

    headers = {
        "Origin": "https://kr.iherb.com",
        "Referer": "https://kr.iherb.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

    print("아이허브 스포츠 스페셜 특가 상품 데이터 수집 시작 (SQLite DB 동시 저장)...")

    while True:
        params = {
            "isMobile": "false",
            "page": page,
            "pageSize": page_size
        }
        query_string = urllib.parse.urlencode(params)
        full_url = f"{base_url}?{query_string}"

        try:
            print(f"페이지 {page} 요청 중...", end="", flush=True)
            html = fetch_page_with_retry(full_url, headers)
            data = json.loads(html)
            
            if "products" not in data or not data["products"]:
                print(" [완료] 더 이상 수집할 상품이 없습니다.")
                break

            products = data["products"]
            num_retrieved = len(products)
            
            # 매 페이지마다 SQLite DB에 즉시 저장
            insert_products_to_db(conn, products)
            print(f" [성공] {num_retrieved}개 수집 및 DB 저장 완료.")

            # 메모리에 전체 데이터 누적 (최종 CSV용)
            for p in products:
                all_products.append({
                    "productId": p.get("productId"),
                    "displayName": p.get("displayName"),
                    "brandName": p.get("brandName"),
                    "listPrice": p.get("listPrice"),
                    "discountPrice": p.get("discountPrice"),
                    "rating": p.get("rating"),
                    "ratingCount": p.get("ratingCount"),
                    "isOutOfStock": p.get("isOutOfStock"),
                    "url": p.get("url")
                })

            if num_retrieved < page_size:
                print(" [완료] 마지막 페이지에 도달했습니다.")
                break

            page += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"\n페이지 {page} 수집 중 오류 발생: {e}")
            break

    # DB 연결 닫기
    conn.close()

    # 전체 데이터 CSV 저장
    total_count = len(all_products)
    if total_count > 0:
        df = pd.DataFrame(all_products)
        df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
        print(f"\n총 {total_count}개의 상품 데이터가 {CSV_PATH}에 저장되었습니다.")
        print(f"SQLite 데이터베이스 저장 완료: {DB_PATH}")
    else:
        print("\n수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
