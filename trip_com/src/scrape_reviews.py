"""
Trip.com 호텔 리뷰 스크래핑 스크립트

목적: scrapling 라이브러리를 사용하여 브라우저처럼 위장(Stealth)하고 Trip.com 호텔 리뷰 API를 호출하여 리뷰(제목, 내용, 별점 등)를 수집합니다.
기능:
1. 첫 번째 페이지 수집 테스트 후 정상 작동 시 CSV 저장
2. 전체 페이지 순회하며 SQLite 데이터베이스에 수집한 리뷰 저장
작성자: Antigravity
생성일: 2026-06-22
"""

import os
import json
import time
import sqlite3
import pandas as pd
from scrapling import Fetcher

# 기본 정보 설정
URL = "https://kr.trip.com/restapi/soa2/34308/getHotelCommentInfo"
HEADERS = {
    "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "w-payload-source": "1.0.9@102!Nudtz1KLhCAbOX4SO6An9PKnG2KLOSqZOlbn+6FaG6OaKSbpKET2OSVbOrK2+ET5+rApbbbpOSknKr42+rG2KlqIbEVbKtb5+rbSOEb2KE4p+rKpOr4nKrq/K5bpOSqL+rk/OSKZKrVpQlVROShDKFO3GVd3hbb=",
    "x-ctx-country": "KR",
    "x-ctx-currency": "KRW",
    "x-ctx-locale": "ko-KR",
    "x-ctx-ubt-pageid": "10320668147",
    "x-ctx-ubt-pvid": "7",
    "x-ctx-ubt-sid": "9",
    "x-ctx-ubt-vid": "1754985737191.9877n1SlbHlt",
    "x-ctx-user-recognize": "NON_EU",
    "x-ctx-wclient-req": "0af33fe7acb74bcfe9f82cf404544b46",
    "Content-Type": "application/json"
}

def get_payload(page_index):
    return {
        "hotelId": 58635410,
        "commentFilterOptions": {
            "pageIndex": page_index,
            "pageSize": 10,
            "repeatComment": 1
        },
        "sceneTypes": ["CommentList"],
        "head": {
            "platform": "PC",
            "cver": "0",
            "cid": "1754985737191.9877n1SlbHlt",
            "bu": "IBU",
            "group": "trip",
            "aid": "",
            "sid": "",
            "ouid": "",
            "locale": "ko-KR",
            "timezone": "9",
            "currency": "KRW",
            "pageId": "10320668147",
            "vid": "1754985737191.9877n1SlbHlt",
            "guid": "",
            "isSSR": False
        }
    }

def extract_comments(data):
    """
    응답 JSON에서 댓글 목록을 추출하고 제목, 내용, 별점을 파싱합니다.
    """
    # 데이터 구조 탐색
    comments_raw = []
    if "comments" in data:
        comments_raw = data["comments"]
    elif "data" in data and "comments" in data["data"]:
        comments_raw = data["data"]["comments"]
    elif "data" in data and "commentList" in data["data"]:
        comments_raw = data["data"]["commentList"]

    parsed_comments = []
    for c in comments_raw:
        # Trip.com 응답의 일반적인 키를 기반으로 추출 (응답 구조에 따라 수정 필요할 수 있음)
        title = c.get("title") or c.get("subject") or "제목 없음"
        content = c.get("content") or c.get("text") or "내용 없음"
        rating = c.get("rating") or c.get("score") or c.get("overallRating") or 0.0
        
        parsed_comments.append({
            "title": title,
            "content": content,
            "rating": rating,
            "raw_data": json.dumps(c, ensure_ascii=False) # 디버깅 및 전체 정보 보존을 위함
        })
    return parsed_comments

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            rating REAL,
            raw_data TEXT
        )
    ''')
    conn.commit()
    return conn

def save_to_db(conn, reviews):
    cursor = conn.cursor()
    for review in reviews:
        cursor.execute('''
            INSERT INTO reviews (title, content, rating, raw_data)
            VALUES (?, ?, ?, ?)
        ''', (review["title"], review["content"], float(review["rating"]), review["raw_data"]))
    conn.commit()

def main():
    # 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    csv_path = os.path.join(data_dir, "trip_reviews_first_page.csv")
    db_path = os.path.join(data_dir, "trip_reviews.db")

    fetcher = Fetcher()
    
    print("=== 1단계: 첫 페이지 수집 테스트 ===")
    page = 1
    payload = get_payload(page)
    response = fetcher.post(URL, headers=HEADERS, json=payload)
    
    if response.status_code != 200:
        print(f"오류: API 요청 실패. 상태 코드: {response.status_code}")
        print("응답:", response.text)
        return

    data = response.json()
    reviews = extract_comments(data)
    
    if not reviews:
        print("오류: 응답에서 리뷰 데이터를 찾을 수 없습니다. JSON 구조를 확인해주세요.")
        print(json.dumps(data, ensure_ascii=False)[:500])
        return
        
    print(f"첫 페이지에서 {len(reviews)}개의 리뷰를 성공적으로 수집했습니다.")
    
    # CSV 저장
    df = pd.DataFrame(reviews)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"첫 페이지 수집 결과 CSV 저장 완료: {csv_path}")
    
    print("\n=== 2단계: 전체 리뷰 수집 및 SQLite 저장 ===")
    conn = init_db(db_path)
    save_to_db(conn, reviews) # 첫 페이지 데이터 저장
    
    page = 2
    
    while True: # 마지막 페이지까지 무한 반복 (더 이상 리뷰가 없으면 종료)
        time.sleep(2) # 서버 부하 방지용 딜레이
        print(f"페이지 {page} 수집 중...")
        
        payload = get_payload(page)
        resp = fetcher.post(URL, headers=HEADERS, json=payload)
        
        if resp.status_code != 200:
            print(f"페이지 {page} 요청 실패. 상태 코드: {resp.status_code}")
            break
            
        page_data = resp.json()
        page_reviews = extract_comments(page_data)
        
        if not page_reviews:
            print(f"페이지 {page}에 더 이상 리뷰가 없거나 추출할 수 없습니다. 수집을 종료합니다.")
            break
            
        save_to_db(conn, page_reviews)
        print(f"페이지 {page}에서 {len(page_reviews)}개 리뷰 수집 및 DB 저장 완료.")
        
        page += 1

    conn.close()
    print(f"\n모든 수집이 완료되었습니다. 데이터는 {db_path} 에 저장되었습니다.")

if __name__ == "__main__":
    main()
