"""
클룩(Klook)에서 한국어 및 원화 설정을 적용하여 상품 데이터를 수집하고
SQLite 데이터베이스(sqlite3)에 실시간(페이지 단위)으로 저장하는 스크레이퍼 스크립트입니다.
페이지 간 0.1~1초 간격으로 무작위 대기를 적용하여 요청을 분산시킵니다.
"""
# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import random
import sqlite3
import pandas as pd
import requests

# 표준 출력 인코딩을 UTF-8로 설정하여 윈도우 cmd/powershell 인코딩 에러(CP949) 방지
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# DB 파일 경로 설정
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SRC_DIR), "data")
DB_PATH = os.path.join(DATA_DIR, "klook_products.db")

def init_db():
    """
    SQLite 데이터베이스 및 테이블을 초기화합니다.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            title TEXT,
            sub_title TEXT,
            price TEXT,
            market_price TEXT,
            city_name TEXT,
            category TEXT,
            rating REAL,
            review_count INTEGER,
            booking_status TEXT,
            deep_link TEXT,
            sold_out INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(products):
    """
    수집된 상품 데이터를 SQLite DB에 INSERT OR REPLACE하고 commit합니다.
    """
    if not products:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for p in products:
        cursor.execute("""
            INSERT OR REPLACE INTO products (
                product_id, title, sub_title, price, market_price, 
                city_name, category, rating, review_count, 
                booking_status, deep_link, sold_out
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(p["product_id"]) if p["product_id"] else None,
            p["title"],
            p["sub_title"],
            p["price"],
            p["market_price"],
            p["city_name"],
            p["category"],
            p["rating"],
            p["review_count"],
            p["booking_status"],
            p["deep_link"],
            1 if p["sold_out"] else 0
        ))
    
    conn.commit()
    conn.close()

def fetch_klook_page(start_page=1, size=15):
    """
    클룩 API를 호출하여 특정 페이지의 상품 데이터를 한국어 설정으로 가져옵니다.
    """
    url = "https://www.klook.com/v1/cardinfocenterservicesrv/search/platform/complete_search_v3"
    
    params = {
        "location": "13,158,46,157,18,156,20544,25723,5031,8928,24975,28741,545,6166,6268,703649,703648,705582,6955,15088,701102,16467,707516,26374,7204,20296,28972,28785,8898,23546,30633,15378,16365,28742,10956,26961,10093,16560,25178,30570,7558,7741,11925,24865,25140,707332,8989,10706,11364,11745,13523,14446,15281,15603,16655,18214,18323,20392,22390,22675,23237,24520,24762,25060,26454,27895,29136,29872,30051,30265,30376,30466,31247,7030,705101,9079",
        "sort": "most_relevant",
        "tab_key": "0",
        "start": str(start_page),
        "query": "대한민국",
        "size": str(size),
        "search_scope": "main_search",
        "k_lang": "ko_KR",
        "k_currency": "KRW"
    }
    
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "referer": "https://www.klook.com/ko/search/result/?query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&search_scope=main_search",
        "x-platform": "desktop",
        "x-requested-with": "XMLHttpRequest",
        "x-klook-user-residence": "10_KR",
        "x-klook-market": "global",
        "x-klook-kepler-id": "a3f03f8c-9dd2-4bb7-b1de-38322eb04cc3",
        "Cookie": "k_lang=ko_KR; k_currency=KRW; currency=KRW; _currency=KRW;",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: HTTP {response.status_code} on page {start_page}")
            return None
    except Exception as e:
        print(f"Exception during request on page {start_page}: {e}")
        return None

def parse_card_data(card):
    """
    개별 상품 카드 데이터에서 필요한 필드들을 안전하게 파싱하여 딕셔너리로 반환합니다.
    """
    data = card.get("data", {})
    
    price_info = data.get("price", {}) or {}
    selling_price = price_info.get("selling_price")
    market_price = price_info.get("market_price")
    
    review_info = data.get("review_obj", {}) or {}
    rating = review_info.get("star")
    review_count = review_info.get("count")
    booked = review_info.get("booked")
    
    return {
        "product_id": data.get("vertical_id"),
        "title": data.get("title"),
        "sub_title": data.get("sub_title"),
        "price": selling_price,
        "market_price": market_price,
        "city_name": data.get("city_name"),
        "category": data.get("category"),
        "rating": rating,
        "review_count": review_count,
        "booking_status": booked,
        "deep_link": data.get("deep_link"),
        "sold_out": data.get("sold_out")
    }

def main():
    print("Klook SQLite DB 기반 데이터 수집 시작...")
    init_db()
    
    # 1페이지를 가져와 전체 아이템 개수 확인
    first_page_data = fetch_klook_page(start_page=1, size=15)
    if not first_page_data:
        print("첫 페이지 데이터를 가져오는데 실패했습니다. 스크립트를 종료합니다.")
        return
        
    total_items = first_page_data.get("result", {}).get("search_result", {}).get("total", 0)
    print(f"전체 수집 대상 상품 수: {total_items}")
    
    if total_items == 0:
        print("수집할 상품이 없습니다.")
        return
        
    page_size = 15
    total_pages = (total_items + page_size - 1) // page_size
    print(f"총 {total_pages}개의 페이지를 수집합니다.")
    
    # 1페이지 데이터 저장
    cards = first_page_data.get("result", {}).get("search_result", {}).get("cards", [])
    first_page_products = []
    for card in cards:
        parsed = parse_card_data(card)
        if parsed["product_id"]:
            first_page_products.append(parsed)
    
    save_to_db(first_page_products)
    print(f"1 페이지 완료: {len(first_page_products)}개 상품 DB 저장됨")
    
    # 2페이지부터 나머지 페이지 순회
    for page in range(2, total_pages + 1):
        # 0.1 ~ 1.0초 무작위 대기 적용
        sleep_time = random.uniform(0.1, 1.0)
        time.sleep(sleep_time)
        
        print(f"페이지 {page} / {total_pages} 수집 중 (대기시간: {sleep_time:.2f}초)...")
        page_data = fetch_klook_page(start_page=page, size=page_size)
        
        if page_data:
            cards = page_data.get("result", {}).get("search_result", {}).get("cards", [])
            page_products = []
            for card in cards:
                parsed = parse_card_data(card)
                if parsed["product_id"]:
                    page_products.append(parsed)
            
            save_to_db(page_products)
            print(f"페이지 {page} 완료: {len(page_products)}개 상품 DB 저장됨")
        else:
            print(f"페이지 {page} 수집 실패, 다음 페이지로 넘어갑니다.")
            
    # 전체 저장된 데이터 개수 조회 및 CSV 백업 업데이트
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        
        # CSV 파일도 최신화
        csv_path = os.path.join(DATA_DIR, "klook_products.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"CSV 파일 백업 완료: {csv_path}")
        print(f"DB에 최종 저장된 상품 수: {len(df)}개")
    except Exception as e:
        print(f"백업 데이터 처리 중 오류 발생: {e}")
        
    print("SQLite DB 저장 데이터 수집이 성공적으로 완료되었습니다!")

if __name__ == "__main__":
    main()
